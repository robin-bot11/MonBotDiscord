# main.py
import discord
from discord.ext import commands
import logging
import asyncio
import os
import importlib.util

# ---------------- DATABASE ----------------
# On utilise storx.py comme Database
from storx import Database

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
    "politique",
    "snipe",
    "partenariat",
    "joinbot",
    "logx",
    "help",
    "papa"  # Owner commands, toujours en dernier
]

# ---------------- UTIL ----------------
async def safe_load_extension(cog_name: str):
    """Charge un cog avec gestion des exceptions et vérifie les dépendances externes"""
    try:
        # Vérifie si le fichier existe avant de charger
        if not importlib.util.find_spec(cog_name):
            logging.warning(f"❌ {cog_name}.py introuvable, passage au suivant")
            return False

        await bot.load_extension(cog_name)
        logging.info(f"✅ {cog_name} chargé ✅")
        return True
    except ModuleNotFoundError as e:
        logging.error(f"❌ {cog_name} nécessite un module manquant : {e.name}")
        return False
    except commands.ExtensionAlreadyLoaded:
        logging.warning(f"{cog_name} déjà chargé, passage au suivant")
        return True
    except Exception as e:
        logging.error(f"❌ Erreur en chargeant {cog_name} : {e}")
        return False

# ---------------- ÉVÉNEMENTS ----------------
@bot.event
async def on_ready():
    logging.info(f"[+] {bot.user} connecté et prêt !")
    # Fallback audit logs pour réduire les risques de logs manqués
    for guild in bot.guilds:
        bot.loop.create_task(fallback_audit_logs(guild))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Vous n'avez pas la permission d'exécuter cette commande.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argument manquant : {error.param}")
    elif isinstance(error, commands.CommandNotFound):
        pass  # ignore
    else:
        logging.error(f"❌ Erreur inattendue : {error}")
        await ctx.send(f"❌ Une erreur est survenue : {error}")

# ---------------- FALLBACK AUDIT LOGS ----------------
async def fallback_audit_logs(guild):
    """Vérifie périodiquement les actions manquées dans audit logs"""
    while True:
        try:
            async for entry in guild.audit_logs(limit=5):
                # Ici tu pourrais traiter les logs manquants, ex: bans/mutes
                pass
        except Exception as e:
            logging.warning(f"⚠️ Audit logs fallback failed: {e}")
        await asyncio.sleep(10)  # toutes les 10s

# ---------------- CHARGEMENT DES COGS ----------------
async def load_cogs():
    for cog in cogs:
        await safe_load_extension(cog)
        # Injecte bot.db si le cog a un attribut db
        ext = bot.get_cog(cog.capitalize())
        if ext and hasattr(ext, "db"):
            setattr(ext, "db", bot.db)

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
