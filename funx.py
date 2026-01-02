# fun.py
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def papa(self, ctx):
        await ctx.send(
            "Mon papa ? 𝐃𝐄𝐔𝐒\n"
            "Le légendaire pilier de ce serveur, inégalable en sagesse et en puissance.\n"
            "Ta présence illumine chaque discussion, et ton charisme inspire tout le monde.\n"
            "Aucun obstacle ne peut t'arrêter, tu es un véritable modèle pour tous !"
        )

# ✅ Correct pour Discord.py 2.x
async def setup(bot):
    await bot.add_cog(Fun(bot))
