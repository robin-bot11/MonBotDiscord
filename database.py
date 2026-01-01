import os
import discord
from discord.ext import commands
import logging
from database import Database

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents, help_command=None)

# --- Token ---
TOKEN = os.getenv("JETON_DISCORD")
if not TOKEN:
    raise ValueError("Le token Discord n'a pas été trouvé !")

# --- Base de données partagée ---
bot.db = Database()

# --- Liste des cogs à charger ---
cogs = [
    "fun",
    "giveaway",
    "aide",
    "verrouiller",
    "journaux",
    "moderation",
    "creator",
    "message_channel",
    "règles",
    "snipe",
    "bienvenue"
]

# --- Chargement automatique des cogs ---
@bot.event
async def setup_hook():
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            logging.info(f"{cog} chargé ✅")
        except Exception as e:
            logging.error(f"Erreur en chargeant {cog} : {e}")

# --- Ready event ---
@bot.event
async def on_ready():
    logging.info(f"[+] {bot.user} est connecté et prêt !")

# --- Run bot ---
bot.run(TOKEN)
