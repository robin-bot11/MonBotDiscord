# main.py
import discord
from discord.ext import commands
import logging
import asyncio
import os

# ---------------- CONFIG ----------------
JETON_DISCORD = os.getenv("JETON_DISCORD")  # Utilisé sur Railway
PREFIX = "+"
intents = discord.Intents.all()

# Désactivation du help par défaut
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---------------- COGS ----------------
# Noms exacts des fichiers .py existants
cogs = [
    "funx",
    "givax",
    "aidx",
    "charlie3",
    "moderation",       # Vérifie que database.py est présent
    "delta4",
    "message_channel",
    "policy",           # Remplace 'politique'
    "snipe",
    "partnership",      # Remplace 'partenariat'
    "joinbot",
    "logx"
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
        await load_cogs()
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
