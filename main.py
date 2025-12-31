import os
import discord
from discord.ext import commands
import logging
import asyncio

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("JETON_DISCORD")
if not TOKEN:
    raise RuntimeError("Token Discord introuvable")

COGS = [
    "fun",
    "giveaway",
    "verrouiller",
    "journaux",
    "moderation",
    "regles",
    "snipe",
    "bienvenue"
]

@bot.event
async def on_ready():
    logging.info(f"{bot.user} est connecté et prêt")

async def load_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            logging.info(f"{cog} chargé")
        except Exception as e:
            logging.error(f"Erreur chargement {cog} : {e}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main())
