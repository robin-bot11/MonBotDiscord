# giveaway.py
from discord.ext import commands, tasks
import discord
import asyncio
from database import Database

COLOR = 0x6b00cb

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.running_giveaways = {}  # stocke les giveaways en cours {message_id: info}

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def gyrole(self, ctx, role: discord.Role):
        """Définir le rôle autorisé à lancer des giveaways"""
        self.db.set_giveaway_role(ctx.guild.id, role.id)
        await ctx.send(embed=discord.Embed(
            description=f"Rôle {role.name} défini pour lancer des giveaways.",
            color=COLOR
        ))

    @commands.command()
    async def gyveaway(self, ctx, duration: int, *, prize):
        """Lancer un giveaway. Durée en minutes."""
        guild_id = ctx.guild.id
        role_id = self.db.get_giveaway_role(guild_id)
        member_roles = [r.id for r in ctx.author.roles]
        if role_id and role_id not in member_roles:
            await ctx.send("Vous n'avez pas le rôle autorisé pour lancer un giveaway.")
            return

        embed = discord.Embed(
            title="🎉 Giveaway !",
            description=f"Récompense : {prize}\nDurée : {duration} minutes",
            color=COLOR
        )
        message = await ctx.send(embed=embed)
        self.running_giveaways[message.id] = {"prize": prize, "author": ctx.author.id}

        await asyncio.sleep(duration * 60)

        try:
            message = await ctx.channel.fetch_message(message.id)
            users = [r async for r in message.reactions[0].users() if not r.bot]
            if users:
                winner = random.choice(users)
                await ctx.send(f"🎉 Félicitations {winner.mention}, vous avez gagné **{prize}** !")
            else:
                await ctx.send("Personne n'a participé au giveaway.")
            del self.running_giveaways[message.id]
        except Exception:
            pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def gyend(self, ctx, message_id: int):
        """Terminer un giveaway avant l'heure"""
        try:
            message = await ctx.channel.fetch_message(message_id)
            await ctx.send(f"Le giveaway pour {self.running_giveaways[message_id]['prize']} est terminé.")
            del self.running_giveaways[message_id]
        except KeyError:
            await ctx.send("Aucun giveaway trouvé avec cet ID.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def gyrestart(self, ctx, message_id: int):
        """Relancer un giveaway terminé"""
        # Ici tu pourrais récupérer les données depuis self.db si tu veux les persister
        await ctx.send("Cette fonction relance le giveaway (à compléter selon la sauvegarde).")

def setup(bot):
    bot.add_cog(Giveaway(bot))
