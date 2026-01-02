import discord
from discord.ext import commands
import logging

# ---------------- CONFIG ----------------
TOKEN = "TON_TOKEN_ICI"
PREFIX = "+"
intents = discord.Intents.all()

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

logging.basicConfig(level=logging.INFO)

# Liste de tous les cogs à charger
cogs = [
    "fun",
    "giveaway",
    "help",
    "lock",
    "logs",
    "moderation",
    "owner",
    "message_channel",
    "policy",
    "snipe",
    "bienvenue",
    "partnership",
    "vérification"
]

# ---------------- ÉVÉNEMENTS ----------------
@bot.event
async def on_ready():
    logging.info(f"[+] {bot.user} est connecté et prêt !")

# ---------------- CHARGEMENT DES COGS ----------------
async def load_cogs():
    for cog in cogs:
        try:
            # Vérifie si le cog est déjà chargé
            if cog in bot.extensions:
                logging.warning(f"{cog} déjà chargé, passage au suivant")
                continue
            await bot.load_extension(cog)
            logging.info(f"{cog} chargé ✅")
        except Exception as e:
            logging.error(f"Erreur en chargeant {cog} : {e}")

# ---------------- MAIN ----------------
async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

import asyncio
asyncio.run(main())
