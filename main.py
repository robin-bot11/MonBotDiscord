import discord
from discord.ext import commands

# Intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

# Ton token ici
TOKEN = "TON_TOKEN_ICI"  # <-- Remplace par ton vrai token

# Liste des cogs à charger
cogs = [
    "moderation",   # commandes de modération : ban, kick, mute, deban, demute, warn, etc.
    "fun",          # commandes publiques : +papa, quote, etc.
    "giveaway",     # commandes de giveaway
    "bienvenue",    # messages de bienvenue et configuration
    "règlement",    # commandes règlement + attribution des rôles
    "journaux",     # système de log : messages, vocal, rôle, membre
    "lock",         # lock/unlock des salons et serveur
    "snipe"         # snipe messages supprimés
]

# Chargement des cogs
for cog in cogs:
    try:
        bot.load_extension(cog)
        print(f"{cog} chargé ✅")
    except Exception as e:
        print(f"Erreur en chargeant {cog} : {e}")

@bot.event
async def on_ready():
    print(f"{bot.user} est connecté et prêt !")

# Démarrage du bot
bot.run(TOKEN)
