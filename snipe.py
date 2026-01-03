from discord.ext import commands
import discord
from datetime import datetime
import time

COLOR = 0x6b00cb
OWNER_ID = 1383790178522370058

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # accès à self.bot.db

    # ------------------ LISTENER ------------------
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        # Enregistre le snipe dans la DB
        self.bot.db.set_snipe(message.channel.id, {
            "author": str(message.author),
            "content": message.content,
            "timestamp": int(time.time())
        })

    # ------------------ SNIPER ------------------
    @commands.command()
    async def snipe(self, ctx):
        """Affiche le dernier message supprimé dans le salon."""
        data = self.bot.db.get_snipe(ctx.channel.id)
        if not data:
            return await ctx.send("Rien à afficher pour le moment dans ce salon !")

        # Convert timestamp en format lisible
        timestamp = datetime.utcfromtimestamp(data["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

        embed = discord.Embed(
            title="Dernier message supprimé",
            description=f"**Auteur :** {data['author']}\n**Message :** {data['content']}\n**Heure (UTC) :** {timestamp}",
            color=COLOR
        )
        await ctx.send(embed=embed)

    # ------------------ PURGE GLOBALE ------------------
    @commands.command()
    async def purge_snipes_global(self, ctx):
        """Supprime tous les snipes de tous les salons (Owner uniquement)."""
        if ctx.author.id != OWNER_ID:
            return await ctx.send("⛔ Vous n'avez pas la permission d'utiliser cette commande.")

        self.bot.db.clear_all_snipes()
        await ctx.send("✅ Tous les snipes ont été supprimés globalement !")

    # ------------------ PURGE SERVEUR ------------------
    @commands.command()
    async def purge_snipes_guild(self, ctx):
        """Supprime tous les snipes du serveur actuel (Owner uniquement)."""
        if ctx.author.id != OWNER_ID:
            return await ctx.send("⛔ Vous n'avez pas la permission d'utiliser cette commande.")

        self.bot.db.clear_guild_snipes(ctx.guild)
        await ctx.send(f"✅ Tous les snipes du serveur **{ctx.guild.name}** ont été supprimés !")

# ------------------ SETUP ------------------
async def setup(bot):
    await bot.add_cog(Snipe(bot))
