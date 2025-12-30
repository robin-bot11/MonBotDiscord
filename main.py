import os
import threading
import discord
from discord.ext import commands
from flask import Flask

# =========================
# Flask (pour Render / UptimeRobot)
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return "MonBotDiscord est en ligne ✅"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

# =========================
# Bot Discord
# =========================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

# =========================
# Token (VARIABLE D’ENVIRONNEMENT)
# =========================
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN manquant dans les variables Render")

# =========================
# Chargement des cogs
# =========================
cogs = [
    "moderation",
    "fun",
    "giveaway",
    "welcome",
    "rules",
    "logs",
    "lock",
    "snipe"
]

@bot.event
async def on_ready():
    print(f"✅ {bot.user} connecté avec succès")

for cog in cogs:
    try:
        bot.load_extension(cog)
        print(f"✔ {cog} chargé")
    except Exception as e:
        print(f"❌ Erreur cog {cog} : {e}")

# =========================
# Lancement du bot
# =========================
bot.run(TOKEN)
