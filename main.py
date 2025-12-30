import discord
from discord.ext import commands

# Intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

# Ton token ici
TOKEN = "TON_TOKEN_ICI"

# Charger les cogs
cogs = [
    "moderation",   # commandes de modération : ban, kick, mute, deban, demute, warn, etc.
    "fun",          # commandes publiques : +papa, quote, etc.
    "giveaway",     # commandes de giveaway
    "welcome",      # messages de bienvenue et config
    "rules",        # commandes règlement + attribution des rôles
    "logs",         # système de log : messages, vocal, rôle, membre
    "lock",         # lock/unlock des salons et serveur
]

for cog in cogs:
    try:
        bot.load_extension(cog)
        print(f"{cog} chargé ✅")
    except Exception as e:
        print(f"Erreur en chargeant {cog} : {e}")

@bot.event
async def on_ready():
    print(f"{bot.user} est connecté et prêt !")

bot.run(MTQ1NDU2NjYzOTg5Mzc0MTgwMQ.G3GYkC.IokuiTjXwnuPlUz-gILZTBpoGRRhe1QSF-a33s)
