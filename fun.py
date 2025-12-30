import discord
from discord.ext import commands, tasks
import asyncio

bot = commands.Bot(command_prefix='+', intents=discord.Intents.all())

# ========================
# COMMANDES PUBLIQUES FUN
# ========================

@bot.command()
async def papa(ctx):
    """Complimente le créateur du bot"""
    message = ("Mon papa ? 𝐃𝐄𝐔𝐒, mon créateur et maître absolu, "
               "le seul qui me guide et m’inspire. Chaque ligne de mon code, "
               "chaque commande que j’exécute n’existe que pour toi et sous ton regard. "
               "Je t’admire et je te suis !")
    await ctx.send(message)

@bot.command()
@commands.has_permissions(administrator=True)
async def timer(ctx, seconds: int, *, message):
    """Envoie un message différé et supprime le message original"""
    await ctx.message.delete()
    await asyncio.sleep(seconds)
    await ctx.send(message)

# ========================
# AJOUTER ICI D'AUTRES COMMANDES FUN PUBLIQUES
# ========================

# Exemple :
# @bot.command()
# async def hello(ctx):
#     await ctx.send(f"Salut {ctx.author.mention} !")

# ========================
# ATTENTION
# ========================
# Ce fichier ne contient pas le token, à mettre dans main.py
