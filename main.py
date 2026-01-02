import os
import discord
from discord.ext import commands
import logging
from database import Database

# ---------------- Logs propres ----------------
logging.basicConfig(level=logging.INFO)

# ---------------- Intents ----------------
intents = discord.Intents.all()

# ---------------- Bot ----------------
bot = commands.Bot(command_prefix="+", intents=intents, help_command=None)

# ---------------- Token ----------------
TOKEN = os.getenv("JETON_DISCORD")
if not TOKEN:
    raise ValueError("Le token Discord n'a pas été trouvé !")

# ---------------- Base de données ----------------
bot.db = Database()  # Singleton pour gérer warns, configs, backup/restore

# ---------------- Liste des cogs ----------------
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
    "welcome",
    "partnership",
    "verification"  # Cog de vérification inclus
]

# ---------------- Chargement des cogs ----------------
@bot.event
async def setup_hook():
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            logging.info(f"{cog} chargé ✅")
        except commands.ExtensionAlreadyLoaded:
            logging.warning(f"{cog} déjà chargé")
        except Exception as e:
            logging.error(f"Erreur en chargeant {cog} : {e}")

# ---------------- Event on_ready ----------------
@bot.event
async def on_ready():
    logging.info(f"[+] {bot.user} est connecté et prêt !")

# ---------------- Lancer le bot ----------------
bot.run(TOKEN)
