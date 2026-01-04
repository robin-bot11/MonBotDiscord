import os
import logging
import asyncio
import importlib.util
import signal

import discord
from discord.ext import commands

# ---------------- ENV ----------------
JETON_DISCORD = os.getenv("JETON_DISCORD")
PREFIX = os.getenv("PREFIX", "+")
BOT_COLOR = int(os.getenv("BOT_COLOR", "0x6b00cb"), 16)
SUCCESS_COLOR = int(os.getenv("SUCCESS_COLOR", "0x00ff00"), 16)

# ---------------- DATABASE ----------------
from storx import DatabasePG

# ---------------- BOT ----------------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)
bot.db: DatabasePG | None = None

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---------------- COGS ----------------
COGS = [
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
    "papa"
]

# ---------------- UTIL ----------------
async def safe_load_extension(cog_name: str):
    try:
        if not importlib.util.find_spec(cog_name):
            logging.warning(f"❌ {cog_name}.py introuvable")
            return

        await bot.load_extension(cog_name)
        logging.info(f"✅ {cog_name} chargé")

        cog = bot.get_cog(cog_name.capitalize())
        if cog and hasattr(cog, "db"):
            cog.db = bot.db

    except commands.ExtensionAlreadyLoaded:
        logging.warning(f"⚠️ {cog_name} déjà chargé")
    except Exception as e:
        logging.error(f"❌ Erreur chargement {cog_name} : {e}")

# ---------------- EVENTS ----------------
@bot.event
async def on_ready():
    logging.info(f"🤖 Connecté en tant que {bot.user} ({bot.user.id})")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Vous n'avez pas la permission.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argument manquant : {error.param.name}")
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        logging.exception("Erreur commande")
        await ctx.send("❌ Une erreur est survenue.")

# ---------------- STARTUP ----------------
async def start_bot():
    if not JETON_DISCORD:
        logging.critical("❌ JETON_DISCORD manquant")
        return

    logging.info("🔄 Connexion à PostgreSQL...")
    bot.db = await DatabasePG.create()
    logging.info("✅ PostgreSQL prêt")

    for cog in COGS:
        await safe_load_extension(cog)

    await bot.start(JETON_DISCORD)

# ---------------- SHUTDOWN ----------------
async def shutdown():
    logging.info("🛑 Arrêt du bot...")
    try:
        if bot.db:
            await bot.db.close()
            logging.info("✅ PostgreSQL fermé")
    except Exception as e:
        logging.error(f"Erreur fermeture DB: {e}")
    await bot.close()

# ---------------- MAIN ----------------
def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(shutdown())
        )

    try:
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

# ---------------- EXEC ----------------
if __name__ == "__main__":
    main()
