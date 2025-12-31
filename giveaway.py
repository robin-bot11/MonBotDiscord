from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_roles = []

    @commands.command()
    async def gyrole(self, ctx, role: discord.Role):
        self.allowed_roles.append(role.id)
        embed = discord.Embed(
            description=f"Rôle autorisé pour les giveaways : {role.mention}",
            color=COLOR
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def gyveaway(self, ctx, duration, *, reward):
        embed = discord.Embed(
            title="🎉 Giveaway lancé",
            description=f"Durée : **{duration}**\nRécompense : **{reward}**",
            color=COLOR
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def gyend(self, ctx, giveaway_id):
        embed = discord.Embed(
            description=f"Giveaway `{giveaway_id}` terminé.",
            color=COLOR
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def gyrestart(self, ctx, giveaway_id):
        embed = discord.Embed(
            description=f"Giveaway `{giveaway_id}` relancé.",
            color=COLOR
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Giveaway(bot))
