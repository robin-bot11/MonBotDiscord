import os
import discord
from discord.ext import commands
import logging
import asyncio

# --- Logs ---
logging.basicConfig(level=logging.INFO)

# --- Couleur des embeds ---
COLOR = 0x6b00cb

# --- Intents ---
intents = discord.Intents.all()

# --- Bot ---
bot = commands.Bot(command_prefix="+", intents=intents, help_command=None)

# --- Token depuis Railway ---
TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("JETON_DISCORD")
if not TOKEN:
    raise ValueError("Le token Discord n'a pas été trouvé ! Assurez-vous qu'il est défini dans Railway.")

# --- Liste des cogs ---
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

# --- Charger tous les cogs correctement ---
async def load_all_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            logging.info(f"{cog} chargé ✅")
        except Exception as e:
            logging.error(f"Erreur en chargeant {cog} : {e}")

# --- Event ready ---
@bot.event
async def on_ready():
    logging.info(f"[ + ] {bot.user} est connecté et prêt !")

# --- Lancer le bot ---
async def main():
    await load_all_cogs()
    await bot.start(TOKEN)

# --- Execution ---
try:
    asyncio.run(main())
except Exception as e:
    logging.error(f"Erreur lors de la connexion du bot : {e}")
