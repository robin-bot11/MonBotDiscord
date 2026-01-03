from discord.ext import commands
import discord
from datetime import datetime, timedelta

COLOR = 0x6b00cb
OWNER_ID = 1383790178522370058
SNIPE_EXPIRATION = timedelta(days=1)

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------ LISTENER ------------------
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild:
            return

        self.bot.db.set_snipe(message.channel.id, {
            "author": str(message.author),
            "content": message.content,
            "time": datetime.utcnow().isoformat()
        })

    # ------------------ COMMANDE SNIPE ------------------
    @commands.command()
    async def snipe(self, ctx):
        data = self.bot.db.get_snipe(ctx.channel.id)
        if not data:
            return await ctx.send("❌ Aucun message supprimé à afficher.")

        timestamp = datetime.fromisoformat(data["time"])
        if datetime.utcnow() - timestamp > SNIPE_EXPIRATION:
            self.bot.db.set_snipe(ctx.channel.id, None)
            return await ctx.send("❌ Le snipe a expiré.")

        embed = discord.Embed(
            title="🕵️ Dernier message supprimé",
            description=(
                f"**Auteur :** {data['author']}\n"
                f"**Message :** {data['content']}\n"
                f"**Heure (UTC) :** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            ),
            color=COLOR
        )
        await ctx.send(embed=embed)

    # ------------------ PURGE SNIPES ------------------
    @commands.command()
    async def purgesnipes(self, ctx, scope: str = None):
        if ctx.author.id != OWNER_ID:
            return await ctx.send("❌ Tu n'es pas autorisé à utiliser cette commande.")

        if scope == "server":
            self.bot.db.clear_guild_snipes(ctx.guild)
            await ctx.send("✅ Tous les snipes du serveur ont été supprimés.")
        else:
            self.bot.db.clear_all_snipes()
            await ctx.send("✅ Tous les snipes ont été supprimés globalement.")

# ------------------ SETUP ------------------
async def setup(bot):
    await bot.add_cog(Snipe(bot))
