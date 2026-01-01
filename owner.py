from discord.ext import commands
import discord

COLOR = 0x6b00cb
OWNER_ID = 1383790178522370058

class Creator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner(self, ctx):
        return ctx.author.id == OWNER_ID

    @commands.command()
    async def ping(self, ctx):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé à utiliser cette commande.")
        await ctx.send("Le bot est en ligne et répond correctement.")

    @commands.command()
    async def dm(self, ctx, user_id: int, *, message):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé à utiliser cette commande.")
        user = await self.bot.fetch_user(user_id)
        try:
            await user.send(message)
            await ctx.send(f"Message envoyé à {user}.")
        except discord.Forbidden:
            await ctx.send("Impossible d'envoyer le message à cet utilisateur.")

    @commands.command()
    async def backupconfig(self, ctx):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé à utiliser cette commande.")
        try:
            self.bot.db.backup()
            await ctx.send("La configuration a été sauvegardée avec succès.")
        except Exception as e:
            await ctx.send(f"Erreur : {e}")

    @commands.command()
    async def restoreconfig(self, ctx):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé à utiliser cette commande.")
        try:
            self.bot.db.restore()
            await ctx.send("La configuration a été restaurée avec succès.")
        except Exception as e:
            await ctx.send(f"Erreur : {e}")

async def setup(bot):
    await bot.add_cog(Creator(bot))
