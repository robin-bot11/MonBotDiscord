import discord
from discord.ext import commands
from flask import Flask
import threading

# --- Serveur Flask pour Render / UptimeRobot ---
app = Flask("")

@app.route("/")
def home():
    return "MonBotDiscord est en ligne !"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

# --- Intents et bot Discord ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

# --- Token du bot ---
TOKEN = "MTQ1NDU2NjYzOTg5Mzc0MTgwMQ.G3GYkC.IokuiTjXwnuPlUz-gILZTBpoGRRhe1QSF-a33s"  # <-- Mets ton vrai token entre les guillemets

# --- Charger les cogs ---
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

for cog in cogs:
    try:
        bot.load_extension(cog)
        print(f"{cog} chargé ✅")
    except Exception as e:
        print(f"Erreur en chargeant {cog} : {e}")

@bot.event
async def on_ready():
    print(f"{bot.user} est connecté et prêt !")

bot.run(TOKEN)
