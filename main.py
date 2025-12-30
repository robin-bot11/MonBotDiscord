# main.py
import discord
from discord.ext import commands
import asyncio

# =======================
# Token et ID du créateur
# =======================
TOKEN = "TON_TOKEN_ICI"  # <-- Mets ton token ici
CREATOR_ID = 1383790178522370058

# Préfixe du bot
bot = commands.Bot(command_prefix="+", intents=discord.Intents.all())

# Import des commandes
import moderation
import giveaways
import welcome
import creator
import utils
import logs

# Chargement des extensions
moderation.setup(bot)
giveaways.setup(bot)
welcome.setup(bot)
creator.setup(bot)
utils.setup(bot)
logs.setup(bot)

# Événement quand le bot est prêt
@bot.event
async def on_ready():
    print(f"{bot.user} est connecté et prêt !")

# Lancer le bot
bot.run(MTQ1NDU2NjYzOTg5Mzc0MTgwMQ.G3GYkC.IokuiTjXwnuPlUz-gILZTBpoGRRhe1QSF-a33s)
