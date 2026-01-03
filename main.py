# main.py
import discord
from discord.ext import commands
import logging
import asyncio
import os
from storx import Database  # ⚠️ Database renommée

# ---------------- CONFIG ----------------
JETON_DISCORD = os.getenv("JETON_DISCORD")
PREFIX = "+"
intents = discord.Intents.all()

# ---------------- BOT ----------------
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)
bot.db = Database()  # Instance unique injectée dans le bot

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

# ---------------- UTILITAIRES ----------------
async def fetch_audit_log_safe(guild, action, limit=5):
    """
    Récupère le dernier audit log d'une action.
    Fallback pour réduire les risques de logs manqués (retry 2s si vide)
    """
    try:
        entry = None
        async for e in guild.audit_logs(limit=limit, action=action):
            entry = e
            break
        if entry is None:
            await asyncio.sleep(2)
            async for e in guild.audit_logs(limit=limit, action=action):
                entry = e
                break
        return entry
    except Exception as e:
        logging.error(f"Erreur fetch_audit_log_safe: {e}")
        return None

def format_success(msg: str) -> str:
    return f"✅ {msg}"

def format_error(msg: str) -> str:
    return f"❌ {msg}"

# ---------------- ÉVÉNEMENTS ----------------
@bot.event
async def on_ready():
    logging.info(format_success(f"{bot.user} connecté et prêt !"))

@bot.event
async def on_command_error(ctx, error):
    """Gestion uniforme des erreurs de commande"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(format_error("Vous n'avez pas la permission d'exécuter cette commande."))
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(format_error(f"Argument manquant : {error.param}"))
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore les commandes inconnues
    else:
        logging.error(f"Erreur inattendue : {error}")
        await ctx.send(format_error(f"Une erreur est survenue : {error}"))

# ---------------- CHARGEMENT DES COGS ----------------
async def load_cogs():
    """Charge tous les cogs et injecte bot.db si nécessaire"""
    for cog_name in cogs:
        try:
            if cog_name in bot.extensions:
                logging.warning(f"{cog_name} déjà chargé, passage au suivant")
                continue

            # Charge le cog
            await bot.load_extension(cog_name)
            cog = bot.get_cog(cog_name.capitalize())

            # Injection automatique de bot.db si le cog a un attribut db
            if cog and hasattr(cog, "db"):
                setattr(cog, "db", bot.db)

            logging.info(format_success(f"{cog_name} chargé ✅"))

        except ModuleNotFoundError:
            logging.warning(f"{cog_name}.py introuvable, passage au suivant")
        except commands.ExtensionAlreadyLoaded:
            logging.warning(f"{cog_name} déjà chargé, passage au suivant")
        except Exception as e:
            logging.error(format_error(f"Erreur en chargeant {cog_name} : {e}"))

# ---------------- MAIN ----------------
async def main():
    if not JETON_DISCORD:
        logging.critical(format_error("Jeton Discord invalide ou manquant !"))
        return

    async with bot:
        await load_cogs()  # Charge tous les cogs avant le start
        try:
            await bot.start(JETON_DISCORD)
        except discord.LoginFailure:
            logging.critical(format_error("Jeton Discord invalide ou manquant !"))
        except Exception as e:
            logging.critical(format_error(f"Erreur lors du démarrage du bot : {e}"))

# ---------------- EXEC ----------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Arrêt manuel du bot.")
    except Exception as e:
        logging.critical(format_error(f"Erreur fatale : {e}"))
