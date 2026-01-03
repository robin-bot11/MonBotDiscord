from discord.ext import commands, tasks
import discord
import asyncio
import random
import re
from datetime import datetime, timedelta
from storx import Database

COLOR = 0x6b00cb
EMOJI = "🎉"
RELAUNCH_DURATION = 0  # Durée fixe non utilisée car relance choisit directement de nouveaux gagnants
BUTTON_TIMEOUT = 12 * 3600  # 12h en secondes


class GiveawayButton(discord.ui.View):
    def __init__(self, bot, msg_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.msg_id = msg_id

    @discord.ui.button(label="Relancer", style=discord.ButtonStyle.success)
    async def relaunch(self, interaction: discord.Interaction, button: discord.ui.Button):
        giveaway_cog = self.bot.get_cog("Giveaway")
        await giveaway_cog.relaunch_giveaway(self.msg_id, interaction)


class Giveaway(commands.Cog):
    """Gestion complète des giveaways avec multi-gagnants et boutons"""

    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.giveaways = self.db.data.get("giveaways", {})
        self.resume_task.start()

    # ================= DURÉE =================
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

    # ================= CREATE GIVEAWAY =================
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
            title="GIVEAWAY",
            description=(
                f"🎁 **Prix :** {prize}\n"
                f"🎯 **Gagnants :** {winners}\n"
                f"👥 **Participants :** 0\n\n"
                f"⏳ **Fin :** <t:{ts}:R>\n"
                f"👤 **Organisé par :** {ctx.author.mention}"
            ),
            color=COLOR
        )

        msg = await ctx.send(embed=embed, view=GiveawayButton(self.bot, 0))  # temporaire view
        await msg.add_reaction(EMOJI)

        # Stockage dans la DB
        self.giveaways[str(msg.id)] = {
            "channel_id": ctx.channel.id,
            "guild_id": ctx.guild.id,
            "end": end_time.timestamp(),
            "winners": winners,
            "prize": prize,
            "host": ctx.author.id,
            "ended": False
        }
        self.db.data["giveaways"] = self.giveaways
        self.db.save()

        # Ajouter la view avec ID correct
        await msg.edit(view=GiveawayButton(self.bot, msg.id))

        self.bot.loop.create_task(self.wait_end(msg.id))

    # ================= PARTICIPANTS LIVE =================
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

    # ================= ATTENTE FIN =================
    async def wait_end(self, msg_id):
        data = self.giveaways.get(str(msg_id))
        if not data:
            return

        delay = data["end"] - datetime.utcnow().timestamp()
        if delay > 0:
            await asyncio.sleep(delay)

        if not data["ended"]:
            await self.validate_giveaway(msg_id)

    # ================= VALIDATION =================
    @commands.command()
    async def gyvalidate(self, ctx, message_id: int):
        await self.validate_giveaway(message_id, manual=True)

    async def validate_giveaway(self, msg_id, manual=False):
        data = self.giveaways.get(str(msg_id))
        if not data:
            return

        channel = self.bot.get_channel(data["channel_id"])
        if not channel:
            del self.giveaways[str(msg_id)]
            self.db.data["giveaways"] = self.giveaways
            self.db.save()
            return

        msg = await channel.fetch_message(msg_id)
        users = set()
        for r in msg.reactions:
            if str(r.emoji) == EMOJI:
                async for u in r.users():
                    if not u.bot:
                        users.add(u)

        if not users:
            await channel.send("❌ Personne n'a participé au giveaway...")
            del self.giveaways[str(msg_id)]
            self.db.data["giveaways"] = self.giveaways
            self.db.save()
            return

        winners = random.sample(list(users), min(len(users), data["winners"]))
        mentions = ", ".join(w.mention for w in winners)

        # Embed annonce
        guild = self.bot.get_guild(data["guild_id"])
        host = guild.get_member(data["host"]) if guild else None
        embed = discord.Embed(
            title="GIVEAWAY TERMINÉ",
            description=(
                f"Le giveaway créé sur le serveur **{guild.name if guild else 'serveur inconnu'}** est maintenant terminé !\n\n"
                f"Le gagnant est {mentions}.\n"
                f"La récompense promise était : **{data['prize']}**."
            ),
            color=COLOR
        )
        await channel.send(embed=embed)

        # DM gagnants
        for w in winners:
            try:
                await w.send(f"🎉 Félicitations ! Tu as gagné un **{data['prize']}** sur {guild.name} !")
            except:
                pass

        # DM organisateur
        if host:
            try:
                await host.send(
                    f"Le giveaway que tu as lancé sur **{guild.name}** est terminé.\n"
                    f"Le gagnant est {mentions}.\n"
                    f"Récompense : **{data['prize']}**"
                )
            except:
                pass

        # Supprimer giveaway
        del self.giveaways[str(msg_id)]
        self.db.data["giveaways"] = self.giveaways
        self.db.save()

    # ================= RELAUNCH =================
    async def relaunch_giveaway(self, msg_id, interaction):
        data = self.giveaways.get(str(msg_id))
        if not data or data["ended"]:
            await interaction.response.send_message("❌ Giveaway déjà terminé.", ephemeral=True)
            return

        channel = self.bot.get_channel(data["channel_id"])
        msg = await channel.fetch_message(msg_id)

        users = set()
        for r in msg.reactions:
            if str(r.emoji) == EMOJI:
                async for u in r.users():
                    if not u.bot:
                        users.add(u)

        if not users:
            await interaction.response.send_message("❌ Personne n'a participé au giveaway...", ephemeral=True)
            return

        winners = random.sample(list(users), min(len(users), data["winners"]))
        mentions = ", ".join(w.mention for w in winners)

        embed = discord.Embed(
            title="GIVEAWAY RELANCÉ",
            description=(
                f"🎯 Nouveau gagnant(s) : {mentions}\n"
                f"La récompense était : **{data['prize']}**"
            ),
            color=COLOR
        )
        await interaction.response.edit_message(embed=embed, view=None)

        # DM gagnants
        guild = self.bot.get_guild(data["guild_id"])
        for w in winners:
            try:
                await w.send(f"🎉 Félicitations ! Tu es le nouveau gagnant du giveaway pour **{data['prize']}** sur {guild.name} !")
            except:
                pass

        # DM organisateur
        host = guild.get_member(data["host"]) if guild else None
        if host:
            try:
                await host.send(
                    f"Le giveaway que tu as lancé sur **{guild.name}** a été relancé.\n"
                    f"Nouveau gagnant : {mentions}\n"
                    f"Récompense : **{data['prize']}**"
                )
            except:
                pass

        # Marque comme terminé
        data["ended"] = True
        self.db.data["giveaways"] = self.giveaways
        self.db.save()

    # ================= REBOOT =================
    @tasks.loop(seconds=10)
    async def resume_task(self):
        await self.bot.wait_until_ready()
        for msg_id in list(self.giveaways.keys()):
            data = self.giveaways[msg_id]
            if not data["ended"]:
                self.bot.loop.create_task(self.wait_end(int(msg_id)))

    @resume_task.before_loop
    async def before_resume(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Giveaway(bot))
