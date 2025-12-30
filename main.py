import os
import discord
from discord.ext import commands
from flask import Flask
import threading

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot en ligne ✅"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask, daemon=True).start()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

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
async def setup_hook():
    for cog in cogs:
        await bot.load_extension(cog)
        print(f"{cog} chargé ✅")

@bot.event
async def on_ready():
    print(f"{bot.user} prêt 🚀")

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN manquant")

bot.run(TOKEN)
