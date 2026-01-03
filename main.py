# main.py
import discord
from discord.ext import commands
import logging
import asyncio
import os

from database import Database  # Assure-toi que database.py est présent

# ---------------- CONFIG ----------------
JETON_DISCORD = os.getenv("JETON_DISCORD")  # Utilisé sur Railway
PREFIX = "+"
intents = discord.Intents.all()

# ---------------- BOT ----------------
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)
bot.db = Database()  # Instance unique de Database injectée dans le bot

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---------------- COGS ----------------
cogs = [
    "funx",
    "givax",
    "aidx",
    "charlie3",
    "moderation",
    "delta4",
    "message_channel",
    "policy",
    "snipe",
    "partnership",
    "joinbot",
    "logx",
    "help"  # Toujours charger le help en dernier
]

# ---------------- ÉVÉNEMENTS ----------------
@bot.event
async def on_ready():
    logging.info(f"[+] {bot.user} connecté et prêt !")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Vous n'avez pas la permission d'exécuter cette commande.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argument manquant : {error.param}")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore les commandes inconnues
    else:
        logging.error(f"Erreur inattendue : {error}")
        await ctx.send(f"❌ Une erreur est survenue : {error}")

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
        # Charge tous les cogs avant de démarrer
        await load_cogs()

        # Démarrage du bot
        try:
            await bot.start(JETON_DISCORD)
        except discord.LoginFailure:
            logging.critical("❌ Jeton Discord invalide ou manquant !")
        except Exception as e:
            logging.critical(f"❌ Erreur lors du démarrage du bot : {e}")

# ---------------- EXEC ----------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Arrêt manuel du bot.")
    except Exception as e:
        logging.critical(f"Erreur fatale : {e}")
