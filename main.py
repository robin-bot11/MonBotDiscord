import discord
from discord.ext import commands
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

INTENTS = discord.Intents.all()

bot = commands.Bot(
    command_prefix="+",
    intents=INTENTS,
    help_command=None
)

COGS = [
    "fun",
    "giveaway",
    "aide",
    "verrouiller",
    "journaux",
    "moderation",
    "règles",
    "snipe",
    "bienvenue"
]

@bot.event
async def on_ready():
    print(f"[ + ] {bot.user} est connecté et prêt !")

async def load_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"{cog} chargé ✅")
        except Exception as e:
            print(f"Erreur chargement {cog} ❌ -> {e}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("JETON_DISCORD"))

asyncio.run(main())
