import discord
from discord.ext import commands

class Reglement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reglement(self, ctx, titre, texte, role: discord.Role):
        embed = discord.Embed(title=titre, description=texte, color=0x6b00cb)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")  # Pour accepter
        await ctx.send(f"Le rôle {role.name} sera donné aux membres acceptant le règlement.")

def setup(bot):
    bot.add_cog(Reglement(bot))
