import discord
from discord.ext import commands

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_roles = {}  # {guild_id: role_id}

    @commands.command()
    async def set_giveaway_role(self, ctx, role: discord.Role):
        self.allowed_roles[ctx.guild.id] = role.id
        await ctx.send(f"Le rôle autorisé pour les giveaways est maintenant {role.name}")

    @commands.command()
    async def giveaway(self, ctx, *, prize=None):
        role_id = self.allowed_roles.get(ctx.guild.id)
        if role_id and not any(role.id == role_id for role in ctx.author.roles):
            await ctx.send("Vous n'avez pas le rôle pour faire un giveaway.")
            return
        embed = discord.Embed(title="🎉 Giveaway 🎉", description=prize or "Pas de description", color=0x6b00cb)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Giveaway(bot))
