from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reglement(self, ctx, titre, texte, role="aucun"):
        await ctx.send(f"Règlement : **{titre}**\n{texte}\nRôle à attribuer : {role}")

def setup(bot):
    bot.add_cog(Rules(bot))
