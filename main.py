import os
import discord
from discord.ext import commands
import logging

from database import Database  # Notre base de données pour sauvegardes

# --- Logs propres ---
logging.basicConfig(level=logging.INFO)

# --- Intents ---
intents = discord.Intents.all()

# --- Bot ---
bot = commands.Bot(command_prefix="+", intents=intents, help_command=None)

# --- Token depuis variable d'environnement ---
TOKEN = os.getenv("JETON_DISCORD")
if not TOKEN:
    raise ValueError("Le token Discord n'a pas été trouvé !")

# --- Base de données ---
db = Database()  # Singleton pour gérer les configs, warns, etc.

# --- Liste des cogs à charger ---
cogs = [
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

for cog in cogs:
    try:
        bot.load_extension(cog)
        logging.info(f"{cog} chargé ✅")
    except Exception as e:
        logging.error(f"Erreur en chargeant {cog} : {e}")

# --- Event on_ready ---
@bot.event
async def on_ready():
    logging.info(f"[ + ] {bot.user} est connecté et prêt !")

# --- Lancer le bot ---
try:
    bot.run(TOKEN)
except Exception as e:
    logging.error(f"Erreur lors de la connexion du bot : {e}")
