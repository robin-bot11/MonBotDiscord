# main.py
import os
import discord
from discord.ext import commands
import logging

# --- Logs propres ---
logging.basicConfig(level=logging.INFO)

# --- Intents ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents, help_command=None)

# --- Token Discord ---
TOKEN = os.getenv("JETON_DISCORD")
if not TOKEN:
    raise ValueError("Le token Discord n'a pas été trouvé !")

# --- Base de données ---
import database

# --- Liste des Cogs ---
cogs = [
    "fun",
    "giveaway",
    "aide",
    "verrouiller",
    "journaux",
    "moderation",
    "règles",
    "snipe",
    "bienvenue"
]

# --- Charger les cogs proprement ---
for cog in cogs:
    try:
        bot.load_extension(cog)
        logging.info(f"{cog} chargé ✅")
    except Exception as e:
        logging.error(f"Erreur en chargeant {cog} : {e}")

# --- Event ready ---
@bot.event
async def on_ready():
    logging.info(f"[ + ] {bot.user} est connecté et prêt !")

# --- Event pour erreurs de commandes ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Vous n'avez pas les permissions pour utiliser cette commande.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Argument manquant pour cette commande.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Commande introuvable.")
    else:
        await ctx.send(f"Erreur : {error}")

# --- Lancer le bot ---
bot.run(TOKEN)
