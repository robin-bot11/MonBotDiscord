# main.py
import os
import logging
import asyncio
import importlib.util

import discord
from discord.ext import commands
from dotenv import load_dotenv

# ---------------- ENV ----------------
load_dotenv()  # Charge automatiquement le fichier .env

JETON_DISCORD = os.getenv("JETON_DISCORD")
DATABASE_URL = os.getenv("DATABASE_URL") or "postgres://user:password@host:port/database"
PREFIX = os.getenv("PREFIX") or "+"
BOT_COLOR = int(os.getenv("BOT_COLOR", "0x6b00cb"), 16)       # violet principal
SUCCESS_COLOR = int(os.getenv("SUCCESS_COLOR", "0x00ff00"), 16)  # vert pour succès
SNIPE_EXPIRATION = int(os.getenv("SNIPE_EXPIRATION", 86400))   # 24h en secondes

# ---------------- DATABASE ----------------
from db_postgres import DatabasePG

# ---------------- BOT ----------------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)
bot.db = None  # sera initialisé plus tard avec PostgreSQL

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---------------- COGS ----------------
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
            ext.db = bot.db  # injecte l'instance PostgreSQL

# ---------------- MAIN ----------------
async def main():
    if not JETON_DISCORD:
        logging.critical("❌ Jeton Discord manquant !")
        return

    # Initialisation PostgreSQL
    logging.info("🔄 Connexion à PostgreSQL...")
    bot.db = await DatabasePG.create(DATABASE_URL)
    logging.info("✅ PostgreSQL connecté et tables prêtes")

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
