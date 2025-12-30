from discord.ext import commands

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gyveaway(self, ctx):
        await ctx.send("Commande +gyveaway activée !")

def setup(bot):
    bot.add_cog(Giveaway(bot))
