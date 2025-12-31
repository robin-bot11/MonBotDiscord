import os
import discord
from discord.ext import commands
import logging

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("JETON_DISCORD")
if not TOKEN:
    raise ValueError("Token Discord introuvable")

cogs = [
    "fun",
    "giveaway",
    "lock",
    "logs",
    "moderation",
    "rules",
    "snipe",
    "welcome"
]

for cog in cogs:
    bot.load_extension(cog)

@bot.event
async def on_ready():
    print(f"{bot.user} prêt")

@bot.command()
async def help(ctx):
    pages = [
        "**MODÉRATION**\n+ban\n+uban\n+kick",
        "**GIVEAWAY**\n+gyrole\n+gyveaway\n+gyend\n+gyrestart",
        "**UTILITAIRES**\n+lock\n+unlock\n+snipe\n+papa"
    ]

    for page in pages:
        embed = discord.Embed(description=page, color=0x6b00cb)
        await ctx.author.send(embed=embed)

bot.run(TOKEN)
