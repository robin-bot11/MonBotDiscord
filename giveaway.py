from discord.ext import commands

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gyveaway(self, ctx, duree=None, *, recompense=None):
        await ctx.send(f"Giveaway lancé pour `{recompense}` pendant `{duree}`.")

    @commands.command()
    async def gyrole(self, ctx, role_id: int):
        await ctx.send(f"Rôle autorisé à lancer des giveaways défini : <@&{role_id}>")

    @commands.command()
    async def gyend(self, ctx, giveaway_id):
        await ctx.send(f"Giveaway `{giveaway_id}` terminé.")

    @commands.command()
    async def gyrestart(self, ctx, giveaway_id):
        await ctx.send(f"Giveaway `{giveaway_id}` relancé.")

def setup(bot):
    bot.add_cog(Giveaway(bot))
