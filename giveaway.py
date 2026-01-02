from discord.ext import commands
import discord
import asyncio
import random
from datetime import datetime, timedelta
from database import Database

COLOR = 0x6b00cb

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.active_giveaways = {}  # msg_id : data

    # ------------------ GYROLE ------------------
    @commands.command()
    async def gyrole(self, ctx, role: discord.Role):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("Vous n'avez pas la permission de définir les rôles autorisés.")
        self.db.add_gyrole(ctx.guild.id, role.id)
        await ctx.send(f"Le rôle {role.name} peut maintenant lancer des giveaways.")

    # ------------------ GYVEAWAY ------------------
    @commands.command()
    async def gyveaway(self, ctx, durée: str, *, récompense: str):
        allowed_roles = self.db.get_gyroles(ctx.guild.id)
        if not any(r.id in allowed_roles for r in ctx.author.roles) and not ctx.author.guild_permissions.administrator:
            return await ctx.send("Vous n'avez pas la permission de lancer un giveaway.")

        time_seconds = self.convert_duration(durée)
        if time_seconds <= 0:
            return await ctx.send("Durée invalide ! Exemple : 1h, 30m")

        embed = discord.Embed(
            title="🎉 Giveaway !",
            description=f"Récompense : {récompense}\nLancé par : {ctx.author.mention}\nDurée : {durée}",
            color=COLOR
        )
        msg = await ctx.send(embed=embed)
        self.active_giveaways[msg.id] = {
            "reward": récompense,
            "author": ctx.author,
            "end_time": datetime.utcnow() + timedelta(seconds=time_seconds)
        }
        await msg.add_reaction("🎉")
        await ctx.send(f"Le giveaway pour **{récompense}** est lancé ! Réagissez avec 🎉 pour participer.")

        self.bot.loop.create_task(self.end_giveaway(msg.id, time_seconds))

    # ------------------ END GIVEAWAY ------------------
    async def end_giveaway(self, msg_id, delay):
        await asyncio.sleep(delay)
        giveaway = self.active_giveaways.get(msg_id)
        if not giveaway:
            return
        channel = giveaway['author'].guild.text_channels[0]
        msg = await channel.fetch_message(msg_id)
        users = set()
        for reaction in msg.reactions:
            if str(reaction.emoji) == "🎉":
                async for user in reaction.users():
                    if not user.bot:
                        users.add(user)
        if not users:
            await channel.send("Personne n'a participé au giveaway...")
            self.active_giveaways.pop(msg_id)
            return

        gagnant = random.choice(list(users))
        await channel.send(f"Félicitations {gagnant.mention} ! Tu as gagné : **{giveaway['reward']}** 🎉")
        try:
            await gagnant.send(f"Félicitations ! Tu as gagné le giveaway pour **{giveaway['reward']}** sur {channel.guild.name} !")
        except:
            pass
        self.active_giveaways.pop(msg_id)

    # ------------------ GYEND ------------------
    @commands.command()
    async def gyend(self, ctx, msg_id: int):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("Seuls les administrateurs peuvent terminer un giveaway manuellement.")
        if msg_id not in self.active_giveaways:
            return await ctx.send("Aucun giveaway actif avec cet ID.")
        await self.end_giveaway(msg_id, 0)
        await ctx.send("Le giveaway a été terminé manuellement.")

    # ------------------ GYRESTART ------------------
    @commands.command()
    async def gyrestart(self, ctx, msg_id: int):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("Seuls les administrateurs peuvent relancer un giveaway.")
        if msg_id not in self.active_giveaways:
            return await ctx.send("Aucun giveaway actif avec cet ID.")
        durée_restante = (self.active_giveaways[msg_id]['end_time'] - datetime.utcnow()).total_seconds()
        if durée_restante < 0:
            durée_restante = 10
        await ctx.send(f"Le giveaway pour **{self.active_giveaways[msg_id]['reward']}** est relancé !")
        self.bot.loop.create_task(self.end_giveaway(msg_id, durée_restante))

    # ------------------ Helper ------------------
    def convert_duration(self, durée: str) -> int:
        try:
            if durée.endswith("h"):
                return int(durée[:-1]) * 3600
            elif durée.endswith("m"):
                return int(durée[:-1]) * 60
            elif durée.endswith("s"):
                return int(durée[:-1])
        except:
            return 0
        return 0

# ------------------ Setup ------------------
async def setup(bot):
    await bot.add_cog(Giveaway(bot))
