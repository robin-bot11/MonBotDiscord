import discord
from discord.ext import commands
import logging
import asyncio
import os

# ---------------- CONFIG ----------------
JETON_DISCORD = os.getenv("JETON_DISCORD")  # Variable d'environnement Railway
PREFIX = "+"
intents = discord.Intents.all()

# Désactivation du help par défaut
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ---------------- COGS ----------------
# Les noms doivent correspondre exactement aux fichiers sans .py
cogs = [
    "funx",
    "givax",
    "aidx",
    "verrouiller",
    "charlie3",
    "moderation",
    "delta4",
    "message_channel",
    "politique",
    "snipe",
    "partenariat",
    "alpha1",
    "joinbot",
    "logx"
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
    if not JETON_DISCORD:
        logging.critical("❌ Jeton Discord invalide ou manquant !")
        return

    async with bot:
        await load_cogs()
        try:
            await bot.start(JETON_DISCORD)
        except discord.LoginFailure:
            logging.critical("❌ Jeton Discord invalide ou manquant !")
        except Exception as e:
            logging.critical(f"❌ Erreur lors du démarrage du bot : {e}")

# ---------------- EXEC ----------------
if __name__ == "__main__":
    asyncio.run(main())
