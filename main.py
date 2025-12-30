import discord
from discord.ext import commands
from flask import Flask
import threading

# ---------- Serveur web minimal pour Render / UptimeRobot ----------
app = Flask("")

@app.route("/")
def home():
    return "Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# Lancer le serveur web
keep_alive()

# ---------- Bot Discord ----------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

# Ton token ici
TOKEN = "TON_TOKEN_ICI"

# Liste des cogs / fichiers avec les commandes
cogs = [
    "moderation",   # commandes de modération : ban, kick, mute, deban, demute, warn, etc.
    "fun",          # commandes publiques : +papa, quote, etc.
    "giveaway",     # commandes de giveaway
    "welcome",      # messages de bienvenue et config
    "rules",        # commandes règlement + attribution des rôles
    "logs",         # système de log : messages, vocal, rôle, membre
    "lock",         # lock/unlock des salons et serveur
    "snipe",        # commandes snipe
]

# Charger les cogs
for cog in cogs:
    try:
        bot.load_extension(cog)
        print(f"{cog} chargé ✅")
    except Exception as e:
        print(f"Erreur en chargeant {cog} : {e}")

# Événement ready
@bot.event
async def on_ready():
    print(f"{bot.user} est connecté et prêt !")

# Lancer le bot
bot.run(MTQ1NDU2NjYzOTg5Mzc0MTgwMQ.G3GYkC.IokuiTjXwnuPlUz-gILZTBpoGRRhe1QSF-a33s)
