import os
import asyncio
import logging
import signal
import importlib.util

import discord
from discord.ext import commands
from aiohttp import web

from storx import DatabasePG

# =========================
# ENV
# =========================
TOKEN = os.getenv("JETON_DISCORD")
PREFIX = os.getenv("PREFIX", "+")
BOT_COLOR = int(os.getenv("BOT_COLOR", "0x6b00cb"), 16)

# =========================
# LOGS
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# =========================
# BOT
# =========================
intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)

bot.db: DatabasePG | None = None

# =========================
# COGS
# =========================
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

async def load_cogs():
    for cog in COGS:
        try:
            if importlib.util.find_spec(cog):
                await bot.load_extension(cog)
                logging.info(f"{cog} chargé")

                instance = bot.get_cog(cog.capitalize())
                if instance and hasattr(instance, "db"):
                    instance.db = bot.db
            else:
                logging.warning(f"{cog}.py introuvable")
        except Exception as e:
            logging.error(f"Erreur cog {cog} : {e}")

# =========================
# EVENTS
# =========================
@bot.event
async def on_ready():
    logging.info(f"Connecté : {bot.user} ({bot.user.id})")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Permission manquante")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Argument manquant")
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        logging.exception("Erreur commande")
        await ctx.send("Erreur inconnue")

# =========================
# WEB SERVER (Render + UptimeRobot)
# =========================
async def web_server():
    async def handle(request):
        return web.Response(text="Bot en ligne")

    app = web.Application()
    app.router.add_get("/", handle)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 3000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logging.info(f"Serveur web lancé sur le port {port}")

# =========================
# START
# =========================
async def start():
    if not TOKEN:
        logging.critical("JETON_DISCORD manquant")
        return

    bot.db = await DatabasePG.create()
    await load_cogs()

    await asyncio.gather(
        web_server(),
        bot.start(TOKEN)
    )

# =========================
# STOP
# =========================
async def shutdown():
    logging.info("Arrêt du bot")
    if bot.db:
        await bot.db.close()
    await bot.close()

# =========================
# MAIN
# =========================
def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))

    try:
        loop.run_until_complete(start())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

if __name__ == "__main__":
    main()
