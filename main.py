import discord
from discord.ext import commands
import logging
import asyncio
import os

# ---------------- CONFIG ----------------
TOKEN = "TON_TOKEN_ICI"  # Remplace par ton vrai token
PREFIX = "+"
intents = discord.Intents.all()

# ---------------- BOT ----------------
# Désactive la commande help par défaut
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

logging.basicConfig(level=logging.INFO)

# ---------------- LISTE DES COGS ----------------
cogs = [
    "fun",
    "giveaway",
    "help",          # ton help.py personnalisé
    "lock",
    "logs",
    "moderation",
    "owner",
    "message_channel",
    "policy",
    "snipe",
    "bienvenue",
    "partnership",
    "verification"   # vérification.py sans accent pour éviter problème Railway
]

# ---------------- ÉVÉNEMENTS ----------------
@bot.event
async def on_ready():
    logging.info(f"[+] {bot.user} est connecté et prêt !")

# ---------------- CHARGEMENT DES COGS ----------------
async def load_cogs():
    for cog in cogs:
        # Vérifie si le fichier cog existe
        file_name = f"{cog}.py"
        if not os.path.isfile(file_name):
            logging.warning(f"{file_name} introuvable, passage au suivant")
            continue

        # Vérifie si le cog est déjà chargé
        if cog in bot.extensions:
            logging.warning(f"{cog} déjà chargé, passage au suivant")
            continue

        try:
            await bot.load_extension(cog)
            logging.info(f"{cog} chargé ✅")
        except Exception as e:
            logging.error(f"Erreur en chargeant {cog} : {e}")

# ---------------- MAIN ----------------
async def main():
    async with bot:
        await load_cogs()
        try:
            await bot.start(TOKEN)
        except discord.errors.LoginFailure:
            logging.critical("❌ Jeton incorrect ! Vérifie ton TOKEN dans main.py")
        except Exception as e:
            logging.critical(f"❌ Erreur critique lors du démarrage : {e}")

# ---------------- LANCEMENT ----------------
if __name__ == "__main__":
    asyncio.run(main())
