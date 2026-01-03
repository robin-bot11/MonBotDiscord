from discord.ext import commands, tasks
import discord
import asyncio
import random
import re
from datetime import datetime, timedelta
from storx import Database

COLOR = 0x6b00cb
EMOJI = "🎉"
RELAUNCH_DURATION_HOURS = 12  # Durée max avant expiration du bouton relancer


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.giveaways = self.db.get("giveaways", {})
        self.resume_giveaways_task.start()

    # ---------------- DURÉE ----------------
    def parse_duration(self, text):
        regex = r"(\d+)(j|h|m|s|jour|jours|heure|heures|minute|minutes|seconde|secondes)"
        matches = re.findall(regex, text.lower())
        total = 0
        for value, unit in matches:
            value = int(value)
            if unit.startswith("j"):
                total += value * 86400
            elif unit.startswith("h"):
                total += value * 3600
            elif unit.startswith("m"):
                total += value * 60
            elif unit.startswith("s"):
                total += value
        return total

    # ---------------- GYVEAWAY ----------------
    @commands.command()
    async def gyveaway(self, ctx, duration: str, winners: int, *, prize: str):
        if not ctx.author.guild_permissions.manage_guild:
            return await ctx.send("❌ Permission refusée.")

        seconds = self.parse_duration(duration)
        if seconds <= 0:
            return await ctx.send("❌ Durée invalide.")

        end_time = datetime.utcnow() + timedelta(seconds=seconds)
        ts = int(end_time.timestamp())

        embed = discord.Embed(
            title="🎉 GIVEAWAY 🎉",
            description=(
                f"🎁 **Prix :** {prize}\n"
                f"🎯 **Gagnants :** {winners}\n"
                f"👥 **Participants :** 0\n\n"
                f"⏳ **Fin :** <t:{ts}:R>\n"
                f"👤 **Organisé par :** {ctx.author.mention}"
            ),
            color=COLOR
        )

        msg = await ctx.send(embed=embed)
        await msg.add_reaction(EMOJI)

        self.giveaways[str(msg.id)] = {
            "channel_id": ctx.channel.id,
            "guild_id": ctx.guild.id,
            "end": end_time.timestamp(),
            "winners": winners,
            "prize": prize,
            "host": ctx.author.id,
            "ended": False,
            "participants": []
        }
        self.db.set("giveaways", self.giveaways)

        # Tâche de fin
        self.bot.loop.create_task(self.wait_end(msg.id))

    # ---------------- PARTICIPANTS LIVE ----------------
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or str(reaction.emoji) != EMOJI:
            return

        msg_id = str(reaction.message.id)
        if msg_id not in self.giveaways:
            return

        users = set()
        async for u in reaction.users():
            if not u.bot:
                users.add(u.id)
        self.giveaways[msg_id]["participants"] = list(users)
        self.db.set("giveaways", self.giveaways)

        # Update compteur participants
        embed = reaction.message.embeds[0]
        embed.description = re.sub(
            r"👥 \*\*Participants :\*\* \d+",
            f"👥 **Participants :** {len(users)}",
            embed.description
        )
        await reaction.message.edit(embed=embed)

    # ---------------- FIN AUTO ----------------
    async def wait_end(self, msg_id):
        data = self.giveaways.get(str(msg_id))
        if not data or data["ended"]:
            return

        delay = data["end"] - datetime.utcnow().timestamp()
        if delay > 0:
            await asyncio.sleep(delay)

        # Marque comme terminé
        data["ended"] = True
        self.db.set("giveaways", self.giveaways)

        # Sélectionne gagnants
        await self.finish_giveaway(msg_id)

    # ---------------- FIN DU GIVEAWAY ----------------
    async def finish_giveaway(self, msg_id):
        data = self.giveaways.get(str(msg_id))
        if not data:
            return

        channel = self.bot.get_channel(data["channel_id"])
        msg = await channel.fetch_message(int(msg_id))

        participants = data.get("participants", [])
        if not participants:
            await channel.send("❌ Personne n'a participé au giveaway...")
            del self.giveaways[msg_id]
            self.db.set("giveaways", self.giveaways)
            return

        winners = random.sample(participants, min(len(participants), data["winners"]))
        mentions = ", ".join(f"<@{w}>" for w in winners)

        embed = discord.Embed(
            title="🎉 GIVEAWAY TERMINÉ 🎉",
            description=(
                f"🎁 **Prix :** {data['prize']}\n"
                f"🏆 {mentions}\n"
            ),
            color=COLOR
        )
        await msg.edit(embed=embed, view=None)

        # DM + ping
        for w in winners:
            user = await self.bot.fetch_user(w)
            try:
                await user.send(f"🎉 Tu as gagné **{data['prize']}** sur {channel.guild.name}")
            except:
                pass

        # Ajoute le bouton relancer si moins de 12h
        if datetime.utcnow().timestamp() - data["end"] < RELAUNCH_DURATION_HOURS * 3600:
            view = GiveawayRelauchView(self, msg, participants, data["winners"], data["prize"])
            await msg.edit(view=view)

    # ---------------- REBOOT ----------------
    @tasks.loop(count=1)
    async def resume_giveaways_task(self):
        await self.bot.wait_until_ready()
        for msg_id, data in self.giveaways.items():
            if not data["ended"]:
                self.bot.loop.create_task(self.wait_end(int(msg_id)))

# ---------------- BOUTON RELANCER ----------------
class GiveawayRelauchView(discord.ui.View):
    def __init__(self, cog: Giveaway, msg, participants, winners_count, prize):
        super().__init__(timeout=None)
        self.cog = cog
        self.msg = msg
        self.participants = participants
        self.winners_count = winners_count
        self.prize = prize
        self.add_item(GiveawayRelaunchButton(self.cog, self.msg, self.participants, self.winners_count, self.prize))

class GiveawayRelaunchButton(discord.ui.Button):
    def __init__(self, cog, msg, participants, winners_count, prize):
        super().__init__(label="Relancer", style=discord.ButtonStyle.primary)
        self.cog = cog
        self.msg = msg
        self.participants = participants
        self.winners_count = winners_count
        self.prize = prize
        self.creation_time = datetime.utcnow()

    async def callback(self, interaction: discord.Interaction):
        # Expire après 12h
        if (datetime.utcnow() - self.creation_time).total_seconds() > RELAUNCH_DURATION_HOURS * 3600:
            return await interaction.response.send_message("⛔ Ce bouton a expiré.", ephemeral=True)

        if not self.participants:
            return await interaction.response.send_message("❌ Aucun participant restant.", ephemeral=True)

        # Nouveau(s) gagnant(s)
        winners = random.sample(self.participants, min(len(self.participants), self.winners_count))
        mentions = ", ".join(f"<@{w}>" for w in winners)

        embed = discord.Embed(
            title="🎉 GIVEAWAY RELANCÉ 🎉",
            description=(
                f"🎁 **Prix :** {self.prize}\n"
                f"🏆 {mentions}\n"
            ),
            color=COLOR
        )
        await self.msg.edit(embed=embed, view=None)

        # DM + ping
        for w in winners:
            user = await self.cog.bot.fetch_user(w)
            try:
                await user.send(f"🎉 Tu as gagné **{self.prize}** sur {self.msg.guild.name}")
            except:
                pass

        await interaction.response.send_message(f"✅ Nouveau(s) gagnant(s) choisi(s) !", ephemeral=True)


# ---------------- SETUP ----------------
async def setup(bot):
    await bot.add_cog(Giveaway(bot))
