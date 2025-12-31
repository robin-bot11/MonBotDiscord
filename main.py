import os
import discord
from discord.ext import commands

# --- Intents et bot Discord ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

# --- Token du bot depuis la variable d'environnement ---
# Sur Railway, le vrai nom de la variable est JETON_DISCORD
TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("JETON_DISCORD")
if not TOKEN:
    raise ValueError(
        "Le token Discord n'a pas été trouvé ! "
        "Assure-toi que JETON_DISCORD est défini dans Railway."
    )

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
