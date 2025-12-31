import os
import discord
from discord.ext import commands
import logging

# Logs propres
logging.basicConfig(level=logging.INFO)

# Intents et bot Discord
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

# Token du bot depuis la variable d'environnement
TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("JETON_DISCORD")
if not TOKEN:
    raise ValueError(
        "Le token Discord n'a pas été trouvé ! "
        "Assure-toi que JETON_DISCORD est défini dans Railway."
    )

# Charger les cogs
cogs = [
    "moderation",
    "fun",
    "giveaway",
    "welcome",
    "rules",
    "logs",
    "lock",
    "snipe",
    "help_cmd"
]

for cog in cogs:
    try:
        bot.load_extension(cog)
        logging.info(f"{cog} chargé ✅")
    except Exception as e:
        logging.error(f"Erreur en chargeant {cog} : {e}")

# Event on_ready
@bot.event
async def on_ready():
    logging.info(f"{bot.user} est connecté et prêt !")

# Lancer le bot
try:
    bot.run(TOKEN)
except Exception as e:
    logging.error(f"Erreur lors de la connexion du bot : {e}")
