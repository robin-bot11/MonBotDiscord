from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.title = None
        self.text = None
        self.role_id = None
        self.button_text = "Accepter"
        self.button_emoji = None

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reglement(self, ctx, titre, texte, role):
        self.title = titre
        self.text = texte
        self.role_id = None if role.lower() == "aucun" else int(role)
        await ctx.send(embed=discord.Embed(description="Règlement configuré.", color=COLOR))

def setup(bot):
    bot.add_cog(Rules(bot))
