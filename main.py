import discord
from discord.ext import commands
from flask import Flask
import threading
import os

# --- Serveur Flask pour Render / UptimeRobot ---
app = Flask("")

@app.route("/")
def home():
    return "MonBotDiscord est en ligne !"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Lancer Flask dans un thread séparé
threading.Thread(target=run_flask).start()

# --- Intents et bot Discord ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

# --- Récupérer le token depuis la variable d'environnement ---
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("Erreur : la variable d'environnement DISCORD_TOKEN n'est pas définie !")
    exit(1)

# --- Charger les cogs ---
cogs = [
    "moderation",   # commandes de modération : ban, kick, mute, deban, demute, warn, etc.
    "fun",          # commandes publiques : +papa, quote, etc.
    "giveaway",     # commandes de giveaway
    "welcome",      # messages de bienvenue et config
    "rules",        # commandes règlement + attribution des rôles
    "logs",         # système de log : messages, vocal, rôle, membre
    "lock",         # lock/unlock des salons et serveur
    "snipe"         # commande snipe
]

for cog in cogs:
    try:
        bot.load_extension(cog)
        print(f"{cog} chargé ✅")
    except Exception as e:
        print(f"Erreur en chargeant {cog} : {e}")

# --- Event on_ready ---
@bot.event
async def on_ready():
    print(f"{bot.user} est connecté et prêt !")

# --- Lancer le bot ---
bot.run(TOKEN)
