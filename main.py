# main.py
import os
import discord
from discord.ext import commands
import logging
from database import Database

# --- Logs propres ---
logging.basicConfig(level=logging.INFO)

# --- Intents Discord ---
intents = discord.Intents.all()

# --- Bot ---
bot = commands.Bot(command_prefix="+", intents=intents, help_command=None)

# --- Token depuis variable d'environnement ---
TOKEN = os.getenv("JETON_DISCORD")
if not TOKEN:
    raise ValueError("Le token Discord n'a pas été trouvé !")

# --- Base de données partagée ---
bot.db = Database()  # Singleton pour gérer warns, configs, backup/restore

# --- Liste des cogs à charger ---
cogs = [
    "fun",
    "giveaway",
    "help",            # anciennement aide.py
    "lock",            # anciennement verrouiller.py
    "logs",            # anciennement journaux.py
    "moderation",      # anciennement modération.py
    "owner",           # anciennement créateur.py
    "message_channel",
    "policy",          # anciennement règles.py
    "snipe",
    "welcome",         # anciennement bienvenue.py
    "partnership"      # nouveau cog pour le salon partenariat
]

# --- Chargement des cogs (discord.py 2.x) ---
@bot.event
async def setup_hook():
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            logging.info(f"{cog} chargé ✅")
        except Exception as e:
            logging.error(f"Erreur en chargeant {cog} : {e}")

# --- Event on_ready ---
@bot.event
async def on_ready():
    logging.info(f"[+] {bot.user} est connecté et prêt !")

# --- Lancer le bot ---
bot.run(TOKEN)
