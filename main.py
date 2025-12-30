import os
import discord
from discord.ext import commands
from flask import Flask

# =========================
# Serveur Flask pour UptimeRobot
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return "MonBotDiscord is live!"

# =========================
# Bot Discord
# =========================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

# Récupération du token depuis les variables d'environnement
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("Le token Discord n'est pas défini dans les variables d'environnement !")

# Liste des cogs à charger
cogs = [
    "moderation",   # commandes de modération : ban, kick, mute, deban, demute, warn, etc.
    "fun",          # commandes publiques : +papa, quote, etc.
    "giveaway",     # commandes de giveaway
    "welcome",      # messages de bienvenue et config
    "rules",        # commandes règlement + attribution des rôles
    "logs",         # système de log : messages, vocal, rôle, membre
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

# Event ready
@bot.event
async def on_ready():
    print(f"{bot.user} est connecté et prêt !")

# =========================
# Lancer Flask et Discord
# =========================
if __name__ == "__main__":
    # Démarrer Flask en arrière-plan
    from threading import Thread
    Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))).start()

    # Lancer le bot Discord
    bot.run(MTQ1NDU2NjYzOTg5Mzc0MTgwMQ.G3GYkC.IokuiTjXwnuPlUz-gILZTBpoGRRhe1QSF-a33s)
