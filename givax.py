from discord.ext import commands, tasks
from discord.ui import View, Button
import discord
import asyncio
import random
import re
from datetime import datetime, timedelta
from storx import Database

COLOR = 0x6b00cb
EMOJI = "🎉"
RELANCE_LIMIT_HOURS = 24

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.giveaways = self.db.data.get("giveaways", {})
        bot.loop.create_task(self.resume_giveaways())

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

    # ---------------- GIVEAWAY ----------------
    @commands.command()
    async def gyveaway(self, ctx, duration: str, winners: int, *, prize: str):
        """Créer un giveaway"""
        # Vérification permissions
        gyroles = self.db.data.get("gyroles", {}).get(str(ctx.guild.id), [])
        if not any(r.id in gyroles for r in ctx.author.roles) and not ctx.author.guild_permissions.administrator:
            return await ctx.send("❌ Vous n'avez pas la permission de lancer un giveaway.")

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
            "relance_time": None
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

    # ---------------- FIN AUTOMATIQUE ----------------
    async def wait_end(self, msg_id):
        data = self.giveaways.get(str(msg_id))
        if not data:
            return

        delay = data["end"] - datetime.utcnow().timestamp()
        if delay > 0:
            await asyncio.sleep(delay)

        await self.end_giveaway(msg_id)

    # ---------------- FIN GIVEAWAY ----------------
    async def end_giveaway(self, msg_id):
        data = self.giveaways.get(str(msg_id))
        if not data or data.get("ended"):
            return

        channel = self.bot.get_channel(data["channel_id"])
        msg = await channel.fetch_message(int(msg_id))

        # Récup participants
        users = set()
        for reaction in msg.reactions:
            if str(reaction.emoji) == EMOJI:
                async for u in reaction.users():
                    if not u.bot:
                        users.add(u)

        if not users:
            await channel.send("❌ Personne n'a participé au giveaway...")
            data["ended"] = True
            data["relance_time"] = datetime.utcnow().timestamp()
            self.db.save()
            return

        winners = random.sample(list(users), min(len(users), data["winners"]))

        # Annonce gagnants
        mentions = ", ".join(w.mention for w in winners)
        await channel.send(embed=discord.Embed(
            title="GIVEAWAY TERMINÉ",
            description=f"🎉 Félicitations {mentions} ! Vous avez gagné un **{data['prize']}** 🎉",
            color=COLOR
        ))

        # DM gagnants
        for w in winners:
            try:
                await w.send(f"🎉 Tu as gagné **{data['prize']}** sur {channel.guild.name}")
            except:
                pass

        # Ping créateur
        host = self.bot.get_user(data["host"])
        if host:
            await host.send(embed=discord.Embed(
                title="Votre giveaway est terminé !",
                description=(
                    f"Le giveaway sur le serveur **{channel.guild.name}** est terminé.\n"
                    f"Le(s) gagnant(s) : {mentions}\n"
                    f"Récompense : **{data['prize']}**"
                ),
                color=COLOR
            ))

        # Ajouter bouton relancer si < 24h
        relance_view = View()
        if datetime.utcnow().timestamp() - data["end"] <= RELANCE_LIMIT_HOURS*3600:
            btn = Button(label="Relancer", style=discord.ButtonStyle.primary)
            async def relancer_callback(interaction):
                await self.handle_relance(interaction, msg_id)
            btn.callback = relancer_callback
            relance_view.add_item(btn)
            await msg.edit(view=relance_view)

        data["ended"] = True
        data["relance_time"] = datetime.utcnow().timestamp()
        self.db.save()

    # ---------------- RELANCE ----------------
    async def handle_relance(self, interaction, msg_id):
        data = self.giveaways.get(str(msg_id))
        if not data:
            return await interaction.response.send_message("❌ Giveaway introuvable.", ephemeral=True)

        # Vérifie permissions
        gyroles = self.db.data.get("gyroles", {}).get(str(interaction.guild.id), [])
        if not any(r.id in gyroles for r in interaction.user.roles) and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Vous n'avez pas la permission de relancer.", ephemeral=True)

        # Vérifie délai 24h
        if datetime.utcnow().timestamp() - data["end"] > RELANCE_LIMIT_HOURS*3600:
            return await interaction.response.send_message("❌ Ce giveaway ne peut plus être relancé.", ephemeral=True)

        # Nouvelle sélection gagnants
        channel = self.bot.get_channel(data["channel_id"])
        msg = await channel.fetch_message(int(msg_id))

        users = set()
        for reaction in msg.reactions:
            if str(reaction.emoji) == EMOJI:
                async for u in reaction.users():
                    if not u.bot:
                        users.add(u)

        if not users:
            return await interaction.response.send_message("❌ Personne n'a participé.", ephemeral=True)

        winners = random.sample(list(users), min(len(users), data["winners"]))
        mentions = ", ".join(w.mention for w in winners)
        await channel.send(embed=discord.Embed(
            title="GIVEAWAY RELANCÉ",
            description=f"🎉 Félicitations {mentions} ! Vous avez gagné un **{data['prize']}** 🎉",
            color=COLOR
        ))

        # DM gagnants
        for w in winners:
            try:
                await w.send(f"🎉 Tu as gagné **{data['prize']}** sur {channel.guild.name}")
            except:
                pass

        # Supprime bouton après relance
        await msg.edit(view=None)

        data["relance_time"] = datetime.utcnow().timestamp()
        self.db.save()
        await interaction.response.send_message("✅ Giveaway relancé avec succès.", ephemeral=True)

    # ---------------- VALIDATION MANUELLE ----------------
    @commands.command()
    async def gyvalidate(self, ctx, msg_id: int):
        data = self.giveaways.get(str(msg_id))
        if not data:
            return await ctx.send("❌ Giveaway introuvable.")

        # Vérifie permissions
        gyroles = self.db.data.get("gyroles", {}).get(str(ctx.guild.id), [])
        if not any(r.id in gyroles for r in ctx.author.roles) and not ctx.author.guild_permissions.administrator:
            return await ctx.send("❌ Vous n'avez pas la permission de valider ce giveaway.")

        # Vérifie délai 24h
        if datetime.utcnow().timestamp() - data["end"] > RELANCE_LIMIT_HOURS*3600:
            return await ctx.send("❌ Ce giveaway ne peut plus être validé.")

        await self.end_giveaway(msg_id)
        await ctx.send("✅ Giveaway validé et terminé manuellement.")

    # ---------------- REBOOT ----------------
    async def resume_giveaways(self):
        await self.bot.wait_until_ready()
        for msg_id in list(self.giveaways.keys()):
            if not self.giveaways[msg_id].get("ended"):
                self.bot.loop.create_task(self.wait_end(int(msg_id)))

# ---------------- SETUP ----------------
async def setup(bot):
    await bot.add_cog(Giveaway(bot))
