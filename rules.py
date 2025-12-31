from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reglement(self, ctx, *, texte):
        embed = discord.Embed(
            title="Règlement du serveur",
            description=texte,
            color=COLOR
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Rules(bot))
