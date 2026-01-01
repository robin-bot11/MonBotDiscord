import os
import discord
from discord.ext import commands
import logging

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents, help_command=None)

TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("JETON_DISCORD")
if not TOKEN:
    raise ValueError("Le token Discord n'a pas été trouvé !")

COGS = [
    "fun",
    "giveaway",
    "aide",
    "verrouiller",
    "journaux",
    "moderation",
    "regles",
    "snipe"
]

for cog in COGS:
    try:
        bot.load_extension(cog)
        print(f"{cog} chargé ✅")
    except Exception as e:
        print(f"Erreur en chargeant {cog} : {e}")

@bot.event
async def on_ready():
    print(f"{bot.user} est connecté et prêt !")

bot.run(TOKEN)
