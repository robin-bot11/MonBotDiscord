# creator.py
from discord.ext import commands
import discord

COLOR = 0x6b00cb
OWNER_ID = 1383790178522370058

class Creator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------ PING ------------------
    @commands.command()
    async def ping(self, ctx):
        if ctx.author.id != OWNER_ID:
            return await ctx.send("Vous n'êtes pas autorisé à utiliser cette commande.")
        await ctx.send("Le bot est en ligne et répond correctement.")

    # ------------------ DM ------------------
    @commands.command()
    async def dm(self, ctx, user_id: int, *, message):
        if ctx.author.id != OWNER_ID:
            return await ctx.send("Vous n'êtes pas autorisé à utiliser cette commande.")
        user = await self.bot.fetch_user(user_id)
        try:
            await user.send(message)
            await ctx.send(f"Message envoyé à {user}.")
        except:
            await ctx.send("Impossible d'envoyer le message à cet utilisateur.")

    # ------------------ BACKUP CONFIG ------------------
    @commands.command()
    async def backupconfig(self, ctx):
        if ctx.author.id != OWNER_ID:
            return await ctx.send("Vous n'êtes pas autorisé à utiliser cette commande.")
        try:
            # Ici tu appelles ta fonction de backup depuis ta Database
            self.bot.db.backup()  # à adapter selon ton code
            await ctx.send("La configuration a été sauvegardée avec succès.")
        except Exception as e:
            await ctx.send(f"Erreur lors de la sauvegarde : {e}")

    # ------------------ RESTORE CONFIG ------------------
    @commands.command()
    async def restoreconfig(self, ctx):
        if ctx.author.id != OWNER_ID:
            return await ctx.send("Vous n'êtes pas autorisé à utiliser cette commande.")
        try:
            # Ici tu appelles ta fonction de restauration depuis ta Database
            self.bot.db.restore()  # à adapter selon ton code
            await ctx.send("La configuration a été restaurée avec succès.")
        except Exception as e:
            await ctx.send(f"Erreur lors de la restauration : {e}")

def setup(bot):
    bot.add_cog(Creator(bot))
