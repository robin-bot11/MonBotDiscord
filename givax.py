from discord.ext import commands, tasks
import discord
import asyncio
import random
import re
from datetime import datetime, timedelta
from storx import Database

COLOR = 0x6b00cb
EMOJI = "🎉"
RELAUNCH_DURATION = 12 * 3600  # bouton relancer actif max 12h


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.giveaways = self.db.data.get("giveaways", {})
        self.bot.loop.create_task(self.resume_giveaways())

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

    # ---------------- LANCER ----------------
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
            "relaunch_allowed": True
        }
        self.db.data["giveaways"] = self.giveaways
        self.db.save()

        self.bot.loop.create_task(self.wait_end(msg.id))

    # ---------------- PARTICIPANTS LIVE ----------------
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or str(reaction.emoji) != EMOJI:
            return

        msg_id = str(reaction.message.id)
        if msg_id not in self.giveaways:
            return

        users = [u async for u in reaction.users() if not u.bot]
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

        await self.finish_giveaway(msg_id)

    # ---------------- FIN GIVEAWAY / RELANCER ----------------
    async def finish_giveaway(self, msg_id, relaunch=False):
        data = self.giveaways.get(str(msg_id))
        if not data or data["ended"]:
            return

        channel = self.bot.get_channel(data["channel_id"])
        try:
            msg = await channel.fetch_message(int(msg_id))
        except:
            del self.giveaways[str(msg_id)]
            self.db.data["giveaways"] = self.giveaways
            self.db.save()
            return

        users = set()
        for r in msg.reactions:
            if str(r.emoji) == EMOJI:
                async for u in r.users():
                    if not u.bot:
                        users.add(u)

        if not users:
            await channel.send(f"❌ Personne n'a participé au giveaway **{data['prize']}**.")
            del self.giveaways[str(msg_id)]
            self.db.data["giveaways"] = self.giveaways
            self.db.save()
            return

        winners = random.sample(list(users), min(len(users), data["winners"]))
        mentions = ", ".join(w.mention for w in winners)

        await channel.send(
            f"🎉 Félicitations {mentions} ! Vous avez gagné **{data['prize']}** 🎉"
        )

        for w in winners:
            try:
                await w.send(f"🎉 Tu as gagné **{data['prize']}** sur {channel.guild.name}")
            except:
                pass

        data["ended"] = True
        data["relaunch_allowed"] = False
        self.db.data["giveaways"] = self.giveaways
        self.db.save()

        # ---------------- BOUTON RELANCER ----------------
        if not relaunch:
            view = discord.ui.View(timeout=43200)  # bouton actif max 12h
            button = discord.ui.Button(label="Relancer", style=discord.ButtonStyle.success)

            async def relaunch_callback(interaction):
                if not data["relaunch_allowed"]:
                    await interaction.response.send_message("❌ Impossible de relancer.", ephemeral=True)
                    return
                # choisit nouveaux gagnants immédiatement
                await self.finish_giveaway(msg_id, relaunch=True)
                await interaction.response.send_message("🔁 Giveaway relancé avec de nouveaux gagnants !", ephemeral=True)

            button.callback = relaunch_callback
            view.add_item(button)
            await channel.send("🔁 Clique pour relancer le giveaway :", view=view)

        # supprime du DB si relaunch
        if relaunch:
            del self.giveaways[str(msg_id)]
            self.db.data["giveaways"] = self.giveaways
            self.db.save()

    # ---------------- VALIDATION MANUELLE ----------------
    @commands.command()
    async def gyvalidate(self, ctx, msg_id: int):
        if str(msg_id) not in self.giveaways:
            return await ctx.send("❌ Giveaway introuvable.")
        await self.finish_giveaway(msg_id)
        await ctx.send(f"✅ Giveaway {msg_id} terminé manuellement.")

    # ---------------- REBOOT ----------------
    async def resume_giveaways(self):
        await self.bot.wait_until_ready()
        for msg_id in list(self.giveaways.keys()):
            self.bot.loop.create_task(self.wait_end(int(msg_id)))


async def setup(bot):
    await bot.add_cog(Giveaway(bot))
