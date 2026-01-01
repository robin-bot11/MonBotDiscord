import os
import discord
from discord.ext import commands
import logging

# --- Logs propres ---
logging.basicConfig(level=logging.INFO)

# --- Intents ---
intents = discord.Intents.all()

# --- Bot Discord ---
bot = commands.Bot(command_prefix="+", intents=intents, help_command=None)

# --- Token depuis Railway ---
TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("JETON_DISCORD")
if not TOKEN:
    raise ValueError("Le token Discord n'a pas été trouvé ! Assurez-vous qu'il est défini dans Railway.")

# --- Liste des cogs à charger ---
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

# --- Charger les cogs ---
for cog in COGS:
    try:
        bot.load_extension(cog)
        logging.info(f"{cog} chargé ✅")
    except Exception as e:
        logging.error(f"Erreur en chargeant {cog} : {e}")

# --- Event ready ---
@bot.event
async def on_ready():
    logging.info(f"{bot.user} est connecté et prêt !")

# --- Lancer le bot ---
try:
    bot.run(TOKEN)
except Exception as e:
    logging.error(f"Erreur lors de la connexion du bot : {e}")
