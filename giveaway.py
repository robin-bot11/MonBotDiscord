from discord.ext import commands

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def gyrole(self, ctx, role: commands.RoleConverter):
        await ctx.send(f"Rôle autorisé aux giveaways : {role.name}")

    @commands.command()
    async def gyveaway(self, ctx, durée, *, récompense):
        await ctx.send(f"Giveaway lancé pour {durée} : {récompense}")

    @commands.command()
    async def gyend(self, ctx, giveaway_id: int):
        await ctx.send(f"Giveaway {giveaway_id} terminé")

    @commands.command()
    async def gyrestart(self, ctx, giveaway_id: int):
        await ctx.send(f"Giveaway {giveaway_id} relancé")

def setup(bot):
    bot.add_cog(Giveaway(bot))
