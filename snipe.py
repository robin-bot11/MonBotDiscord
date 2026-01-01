# snipe.py
from discord.ext import commands
import discord
from datetime import datetime

COLOR = 0x6b00cb

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # accès à self.bot.db

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        # Sauvegarder le message supprimé dans la DB
        self.bot.db.set_snipe(message.channel.id, {
            "author": str(message.author),
            "content": message.content,
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })

    @commands.command()
    async def snipe(self, ctx):
        """Affiche le dernier message supprimé dans le salon."""
        data = self.bot.db.get_snipe(ctx.channel.id)
        if not data:
            return await ctx.send("Rien à afficher pour le moment dans ce salon !")
        
        embed = discord.Embed(
            title="Dernier message supprimé",
            description=f"**Auteur :** {data['author']}\n**Message :** {data['content']}\n**Heure (UTC) :** {data['time']}",
            color=COLOR
        )
        await ctx.send(embed=embed)

# ✅ Correct pour Discord.py 2.x
async def setup(bot):
    await bot.add_cog(Snipe(bot))
