# aide.py
from discord.ext import commands
import discord

COLOR = 0x6b00cb
OWNER_ID = 1383790178522370058

class Aide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx, page: str = None):
        pages = {
            "modération": {
                "+kick <ID> <raison>": "Expulse un membre. Permission : Kick Members",
                "+ban <ID> <raison>": "Bannit un membre. Permission : Ban Members",
                "+uban <ID>": "Débannit un membre. Permission : Ban Members",
                "+mute <ID> <raison>": "Mute un membre. Permission : Manage Roles",
                "+unmute <ID>": "Démute un membre. Permission : Manage Roles",
                "+warn <ID> <raison>": "Ajoute un avertissement. Permission : Manage Messages",
                "+unwarn <ID> <num_warn>": "Supprime un avertissement. Permission : Manage Messages",
                "+warns <ID>": "Liste les warns d’un membre. Permission : Manage Messages",
                "+purge <nombre>": "Supprime un nombre de messages. Permission : Manage Messages",
                "+purgeall": "Supprime tous les messages du salon. Permission : Administrateur"
            },
            "giveaway": {
                "+gyveaway <durée> <récompense>": "Lance un giveaway. Permission : Rôle défini par +gyrole",
                "+gyrole <ID rôle>": "Définit les rôles autorisés à lancer des giveaways. Permission : Administrateur",
                "+gyend <ID>": "Termine un giveaway. Permission : Rôle défini",
                "+gyrestart <ID>": "Relance un giveaway. Permission : Rôle défini"
            },
            "fun": {
                "+papa": "Commande fun. Permission : Aucune"
            },
            "partenariat": {
                "+setpartnerrole <@rôle>": "Configure le rôle à ping automatiquement lorsqu’un lien d’invitation est posté dans le salon partenariat. Permission : Owner",
            }
        }

        embed = discord.Embed(title="Commandes disponibles", color=COLOR)

        if page:
            page_name = page.lower()
            if page_name in pages:
                cmds = pages[page_name]
                value = "\n".join([f"{cmd} : {desc}" for cmd, desc in cmds.items()])
                embed.add_field(name=page_name.capitalize(), value=value, inline=False)
            else:
                embed.description = "Cette catégorie n'existe pas."
        else:
            for category, cmds in pages.items():
                value = "\n".join([f"{cmd} : {desc}" for cmd, desc in cmds.items()])
                embed.add_field(name=category.capitalize(), value=value, inline=False)

        try:
            await ctx.author.send(embed=embed)
            await ctx.send("Je t'ai envoyé la liste de commandes en MP !")
        except discord.Forbidden:
            await ctx.send(f"{ctx.author.mention}, je n'ai pas pu t'envoyer les commandes en MP.")

async def setup(bot):
    await bot.add_cog(Aide(bot))
