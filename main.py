# main.py
import discord
from discord.ext import commands

intents = discord.Intents.all()  # Pour gérer tous les événements
bot = commands.Bot(command_prefix="+", intents=intents)

# ----- Chargement des extensions/catégories -----
# Chaque fichier représente une catégorie de commandes
extensions = [
    "moderation",   # Ban, Kick, Mute, Deban, Demute, Warn, etc.
    "snipe",        # Commande +snipe
    "giveaway",     # Gestion des giveaways
    "welcome",      # Message de bienvenue et rôles
    "logs",         # Système de logs (messages, salons, vocaux, rôles)
    "fun",          # Commandes fun (+papa etc.)
    "locks",        # Commandes lock/unlock et configuration des salons
    "reglement"     # Commandes pour gérer le règlement
]

for ext in extensions:
    try:
        bot.load_extension(ext)
        print(f"{ext} chargé avec succès !")
    except Exception as e:
        print(f"Erreur lors du chargement de {ext} : {e}")

# ----- Event ready -----
@bot.event
async def on_ready():
    print(f"{bot.user} est connecté et prêt !")

# ----- Token -----
# Remplace "VOTRE_TOKEN_ICI" par ton vrai token Discord
TOKEN = "VOTRE_TOKEN_ICI"
bot.run(MTQ1NDU2NjYzOTg5Mzc0MTgwMQ.G3GYkC.IokuiTjXwnuPlUz-gILZTBpoGRRhe1QSF-a33s)
