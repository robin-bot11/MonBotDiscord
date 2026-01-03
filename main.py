# main.py
import discord
from discord.ext import commands
import logging
import asyncio
import os
import importlib.util

# ---------------- DATABASE ----------------
from storx import Database

# ---------------- CONFIG ----------------
JETON_DISCORD = os.getenv("JETON_DISCORD")
PREFIX = "+"
intents = discord.Intents.all()

# ---------------- BOT ----------------
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)
bot.db = Database()  # Instance unique injectée dans le bot

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---------------- COGS ----------------
# ⚠️ uniquement les fichiers existants
cogs = [
    "funx",
    "givax",
    "aidx",
    "charlie3",
    "moderation",
    "delta4",
    "message_channel",
    "snipe",
    "joinbot",
    "logx",
    "papa"  # Owner commands, toujours en dernier
]

# ---------------- UTIL ----------------
async def safe_load_extension(cog_name: str):
    try:
        if not importlib.util.find_spec(cog_name):
            logging.warning(f"❌ {cog_name}.py introuvable, passage au suivant")
            return False

        await bot.load_extension(cog_name)
        logging.info(f"✅ {cog_name} chargé ✅")
        return True

    except commands.ExtensionAlreadyLoaded:
        logging.warning(f"{cog_name} déjà chargé")
        return True
    except Exception as e:
        logging.error(f"❌ Erreur en chargeant {cog_name} : {e}")
        return False

# ---------------- ÉVÉNEMENTS ----------------
@bot.event
async def on_ready():
    logging.info(f"[+] {bot.user} connecté et prêt !")
    for guild in bot.guilds:
        bot.loop.create_task(fallback_audit_logs(guild))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Vous n'avez pas la permission d'exécuter cette commande.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argument manquant : {error.param}")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        logging.error(f"❌ Erreur inattendue : {error}")
        await ctx.send("❌ Une erreur est survenue.")

# ---------------- FALLBACK AUDIT LOGS ----------------
async def fallback_audit_logs(guild):
    while True:
        try:
            async for _ in guild.audit_logs(limit=5):
                pass
        except Exception as e:
            logging.warning(f"⚠️ Audit logs fallback failed: {e}")
        await asyncio.sleep(10)

# ---------------- CHARGEMENT DES COGS ----------------
async def load_cogs():
    for cog in cogs:
        await safe_load_extension(cog)
        ext = bot.get_cog(cog.capitalize())
        if ext and hasattr(ext, "db"):
            ext.db = bot.db

# ---------------- MAIN ----------------
async def main():
    if not JETON_DISCORD:
        logging.critical("❌ Jeton Discord manquant !")
        return

    async with bot:
        await load_cogs()
        await bot.start(JETON_DISCORD)

# ---------------- EXEC ----------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Arrêt manuel du bot.")
    except Exception as e:
        logging.critical(f"Erreur fatale : {e}")
