# fun.py
from discord.ext import commands

COLOR = 0x6b00cb

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def papa(self, ctx):
        """Compliment au propriétaire du bot"""
        message = (
            "Mon papa ? 𝐃𝐄𝐔𝐒\n"
            "Le légendaire pilier de ce serveur, inégalable en sagesse et en puissance.\n"
            "Ta présence illumine chaque discussion, et ton charisme inspire tout le monde.\n"
            "Aucun obstacle ne peut t'arrêter, tu es un véritable modèle pour tous !"
        )
        await ctx.send(message)

def setup(bot):
    bot.add_cog(Fun(bot))
