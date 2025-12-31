import os
import discord
from discord.ext import commands
import logging
import asyncio

# --- Logs propres ---
logging.basicConfig(level=logging.INFO)

# --- Intents ---
intents = discord.Intents.all()

# --- Bot avec préfixe + et help désactivé ---
bot = commands.Bot(
    command_prefix="+",
    intents=intents,
    help_command=None  # Supprime le help par défaut
)

# --- Token depuis variable d'environnement ---
TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("JETON_DISCORD")
if not TOKEN:
    raise RuntimeError("Le token Discord n'a pas été trouvé !")

# --- Liste des cogs à charger ---
COGS = [
    "help",
    "fun",
    "giveaway",
    "verrouiller",
    "journaux",
    "moderation",
    "regles",
    "snipe",
    "bienvenue"
]

# --- Event on_ready ---
@bot.event
async def on_ready():
    logging.info(f"{bot.user} est connecté et prêt !")

# --- Fonction pour charger les cogs ---
async def load_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            logging.info(f"{cog} chargé ✅")
        except Exception as e:
            logging.error(f"Erreur en chargeant {cog} : {e}")

# --- Main async pour démarrer le bot ---
async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

# --- Lancement du bot ---
asyncio.run(main())
