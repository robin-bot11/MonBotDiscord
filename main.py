import discord
from discord.ext import commands
import logging
import asyncio

# ---------------- CONFIG ----------------
JETON_DISCORD = "TON_TOKEN_ICI"
PREFIX = "+"
intents = discord.Intents.all()

# Désactivation du help par défaut
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

logging.basicConfig(level=logging.INFO)

# ---------------- COGS ----------------
cogs = [
    "funx",
    "givax",
    "aide",
    "verrouiller",
    "charlie3",     # journaux
    "moderation",
    "delta4",       # propriétaire
    "message_channel",
    "politique",
    "snipe",
    "partenariat",
    "logx",
    "joinbot"       # vérification + bienvenue fusionné
]

# ---------------- ÉVÉNEMENTS ----------------
@bot.event
async def on_ready():
    logging.info(f"[+] {bot.user} est connecté et prêt !")

# ---------------- CHARGEMENT DES COGS ----------------
async def load_cogs():
    for cog in cogs:
        try:
            if cog in bot.extensions:
                logging.warning(f"{cog} déjà chargé, passage au suivant")
                continue
            await bot.load_extension(cog)
            logging.info(f"{cog} chargé ✅")
        except ModuleNotFoundError:
            logging.warning(f"{cog}.py introuvable, passage au suivant")
        except commands.ExtensionAlreadyLoaded:
            logging.warning(f"{cog} déjà chargé, passage au suivant")
        except Exception as e:
            logging.error(f"Erreur en chargeant {cog} : {e}")

# ---------------- MAIN ----------------
async def main():
    async with bot:
        await load_cogs()
        try:
            await bot.start(JETON_DISCORD)
        except discord.LoginFailure:
            logging.critical("❌ Jeton Discord invalide ou manquant !")

# ---------------- EXEC ----------------
asyncio.run(main())
