# =============================
# SITE WEB (KEEP ALIVE)
# =============================
from flask import Flask
from threading import Thread

app = Flask(__name__)

BOT_STATUS = {"online": False}

@app.route("/")
def home():
    return "Le bot est en ligne."

@app.route("/status")
def status():
    if BOT_STATUS["online"]:
        return "Bot Discord connecté."
    else:
        return "Bot Discord hors ligne."

def run_site():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run_site)
    t.start()

keep_alive()

# =============================
# BOT DISCORD
# =============================
import discord
from discord.ext import commands
import asyncio
import random
import json

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents, help_command=None)

CREATOR_ID = 1383790178522370058
EMBED_COLOR = 0x7a00ff

config = {
    "welcome_channel": None,
    "welcome_message": None,
    "role_membre": None,
    "giveaway_role": None
}

def save_config():
    with open("config.json", "w") as f:
        json.dump(config, f)

def load_config():
    global config
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except:
        save_config()

load_config()

snipes = {}

# =============================
# EVENTS
# =============================
@bot.event
async def on_ready():
    BOT_STATUS["online"] = True
    print(f"{bot.user} est connecté")

@bot.event
async def on_member_join(member):
    if config["role_membre"]:
        role = member.guild.get_role(config["role_membre"])
        if role:
            await member.add_roles(role)

    if config["welcome_channel"] and config["welcome_message"]:
        channel = member.guild.get_channel(config["welcome_channel"])
        if channel:
            msg = config["welcome_message"] \
                .replace("{user}", member.mention) \
                .replace("{server}", member.guild.name) \
                .replace("{members}", str(member.guild.member_count))
            embed = discord.Embed(description=msg, color=EMBED_COLOR)
            await channel.send(embed=embed)

@bot.event
async def on_message_delete(message):
    snipes[message.channel.id] = message

# =============================
# COMMANDES PUBLIQUES
# =============================
@bot.command()
async def snipe(ctx):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("Vous n'avez pas la permission nécessaire pour utiliser cette commande.")
        return
    msg = snipes.get(ctx.channel.id)
    if not msg:
        await ctx.send("Aucun message supprimé récemment.")
        return
    embed = discord.Embed(description=msg.content, color=EMBED_COLOR)
    embed.set_footer(text=f"Message de {msg.author}")
    await ctx.send(embed=embed)

@bot.command()
async def botinfo(ctx):
    embed = discord.Embed(
        title="Informations du bot",
        description="Créé par Robin",
        color=EMBED_COLOR
    )
    embed.add_field(name="Préfixe", value="+", inline=False)
    embed.add_field(name="Statut", value="En ligne", inline=False)
    await ctx.send(embed=embed)

# =============================
# HELP (EN MP)
# =============================
@bot.command()
async def help(ctx):
    texte = """
Commandes publiques :
+help
+botinfo
+snipe
+timer <secondes> <message>

Commandes modération :
+mute
+unmute

Commandes configuration :
+configwelcome
+setgiveawayrole

Commandes giveaway :
+giveaway
"""
    try:
        await ctx.author.send(texte)
        await ctx.send("La liste des commandes vous a été envoyée en message privé.")
    except:
        await ctx.send("Impossible de vous envoyer un message privé.")

# =============================
# MODÉRATION
# =============================
@bot.command()
async def mute(ctx, member: discord.Member):
    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("Vous n'avez pas la permission nécessaire.")
        return
    role = discord.utils.get(ctx.guild.roles, name="Mute")
    if not role:
        role = await ctx.guild.create_role(name="Mute")
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False, speak=False)
    await member.add_roles(role)
    await ctx.send(f"{member.mention} a été mute.")

@bot.command()
async def unmute(ctx, member: discord.Member):
    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("Vous n'avez pas la permission nécessaire.")
        return
    role = discord.utils.get(ctx.guild.roles, name="Mute")
    if role and role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"{member.mention} a été unmute.")

# =============================
# CONFIGURATION
# =============================
@bot.command()
async def configwelcome(ctx, channel: discord.TextChannel, *, message):
    config["welcome_channel"] = channel.id
    config["welcome_message"] = message
    save_config()
    await ctx.send("Message de bienvenue configuré.")

@bot.command()
async def setgiveawayrole(ctx, role: discord.Role):
    config["giveaway_role"] = role.id
    save_config()
    await ctx.send("Rôle giveaway configuré.")

# =============================
# TIMER MESSAGE
# =============================
@bot.command()
async def timer(ctx, seconds: int, *, message):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Vous n'avez pas la permission nécessaire.")
        return
    await ctx.message.delete()
    await asyncio.sleep(seconds)
    await ctx.send(message)

# =============================
# GIVEAWAY
# =============================
@bot.command()
async def giveaway(ctx, duration: int, *, prize):
    if config["giveaway_role"]:
        role = ctx.guild.get_role(config["giveaway_role"])
        if role not in ctx.author.roles:
            await ctx.send("Vous n'avez pas la permission nécessaire.")
            return
    embed = discord.Embed(
        title="🎉 Giveaway 🎉",
        description=f"Prix : {prize}\nRéagissez avec 🎉",
        color=EMBED_COLOR
    )
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎉")
    await asyncio.sleep(duration)
    msg = await ctx.channel.fetch_message(msg.id)
    users = []
    for reaction in msg.reactions:
        if str(reaction.emoji) == "🎉":
            async for user in reaction.users():
                if not user.bot:
                    users.append(user)
    if users:
        winner = random.choice(users)
        await ctx.send(f"Félicitations {winner.mention}, tu as gagné **{prize}** !")
    else:
        await ctx.send("Aucun participant.")

# =============================
# LANCEMENT DU BOT
# =============================
bot.run(MTQ1NDU2NjYzOTg5Mzc0MTgwMQ.GkxQ5r.EMsrSQkAAAx9_KvfvWS_fvp5bQHTH0cDNQDmOA)