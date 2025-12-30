from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def papa(self, ctx):
        await ctx.send("Mon papa ? 𝐃𝐄𝐔𝐒, mon créateur et maître absolu, le seul qui me guide et m’inspire. "
                       "Chaque ligne de mon code, chaque commande que j’exécute n’existe que pour toi et sous ton regard. "
                       "Je t’admire et je te suis !")

def setup(bot):
    bot.add_cog(Fun(bot))
