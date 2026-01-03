from discord.ext import commands
import discord
import asyncio
import random
from datetime import datetime, timedelta
from storx import Database

COLOR = 0x6b00cb

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.active_giveaways = {}  # msg_id : données du giveaway

    @commands.command()
    async def gyrole(self, ctx, *, role: discord.Role):
        """Définir un rôle autorisé à lancer des giveaways"""
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("❌ Vous n'avez pas la permission de définir les rôles autorisés.")
        self.db.add_gyrole(ctx.guild.id, role.id)
        await ctx.send(f"✅ Le rôle {role.name} peut maintenant lancer des giveaways.")

    @commands.command()
    async def gyveaway(self, ctx, durée: str, *, récompense: str):
        """Lancer un giveaway. Exemple: +gyveaway 30s Nitro"""
        allowed_roles = self.db.get_gyroles(ctx.guild.id) or []
        if not any(r.id in allowed_roles for r in ctx.author.roles) and not ctx.author.guild_permissions.administrator:
            return await ctx.send("❌ Vous n'avez pas la permission de lancer un giveaway.")

        time_seconds = self.convert_duration(durée)
        if time_seconds <= 0:
            return await ctx.send("❌ Durée invalide ! Exemple : 1j, 2h, 30m, 45s")

        embed = discord.Embed(
            title="🎉 Giveaway !",
            description=f"Récompense : **{récompense}**\nLancé par : {ctx.author.mention}\nDurée : {durée}",
            color=COLOR
        )
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎉")

        self.active_giveaways[msg.id] = {
            "reward": récompense,
            "author": ctx.author,
            "end_time": datetime.utcnow() + timedelta(seconds=time_seconds),
            "channel": ctx.channel
        }

        await ctx.send(f"✅ Le giveaway pour **{récompense}** est lancé ! Réagissez avec 🎉 pour participer.")
        self.bot.loop.create_task(self.end_giveaway(msg.id, time_seconds))

    async def end_giveaway(self, msg_id, delay):
        await asyncio.sleep(delay)
        giveaway = self.active_giveaways.get(msg_id)
        if not giveaway:
            return

        channel = giveaway["channel"]
        try:
            msg = await channel.fetch_message(msg_id)
        except:
            self.active_giveaways.pop(msg_id, None)
            return

        users = set()
        for reaction in msg.reactions:
            if str(reaction.emoji) == "🎉":
                async for user in reaction.users():
                    if not user.bot:
                        users.add(user)

        if not users:
            await channel.send("❌ Personne n'a participé au giveaway...")
            self.active_giveaways.pop(msg_id, None)
            return

        gagnant = random.choice(list(users))
        await channel.send(f"🎉 Félicitations {gagnant.mention} ! Tu as gagné : **{giveaway['reward']}**")
        try:
            await gagnant.send(f"🎉 Félicitations ! Tu as gagné le giveaway pour **{giveaway['reward']}** sur {channel.guild.name} !")
        except:
            pass

        self.active_giveaways.pop(msg_id, None)

    @commands.command()
    async def gyend(self, ctx, msg_id: int):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("❌ Seuls les administrateurs peuvent terminer un giveaway manuellement.")
        if msg_id not in self.active_giveaways:
            return await ctx.send("❌ Aucun giveaway actif avec cet ID.")
        await self.end_giveaway(msg_id, 0)
        await ctx.send("✅ Le giveaway a été terminé manuellement.")

    @commands.command()
    async def gyrestart(self, ctx, msg_id: int):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("❌ Seuls les administrateurs peuvent relancer un giveaway.")
        if msg_id not in self.active_giveaways:
            return await ctx.send("❌ Aucun giveaway actif avec cet ID.")

        durée_restante = (self.active_giveaways[msg_id]['end_time'] - datetime.utcnow()).total_seconds()
        if durée_restante < 0:
            durée_restante = 10

        await ctx.send(f"✅ Le giveaway pour **{self.active_giveaways[msg_id]['reward']}** est relancé !")
        self.bot.loop.create_task(self.end_giveaway(msg_id, durée_restante))

    def convert_duration(self, durée: str) -> int:
        """Convertit une durée comme 1j, 2heures, 30m, 45s en secondes"""
        durée = durée.lower().strip()
        try:
            # Extraire le nombre
            number = int(''.join(filter(str.isdigit, durée)))
            if any(x in durée for x in ["jour", "jours", "j"]):
                return number * 86400
            elif any(x in durée for x in ["heure", "heures", "h"]):
                return number * 3600
            elif any(x in durée for x in ["minute", "minutes", "m"]):
                return number * 60
            elif any(x in durée for x in ["seconde", "secondes", "s"]):
                return number
        except:
            return 0
        return 0

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
