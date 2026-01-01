
from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Aide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, page: str = None):
        # Définir les pages par catégorie
        pages = {
            "Modération": [
                "+kick <ID> <raison>",
                "+ban <ID> <raison>",
                "+uban <ID>",
                "+mute <ID> <raison>",
                "+umute <ID>",
                "+warn <ID> <raison>",
                "+uwarn <ID> <num_warn>",
                "+delwarn <ID> <num_warn>",
                "+slowmode <#salon> <durée>"
            ],
            "Giveaway": [
                "+gyveaway <durée> <récompense>",
                "+gyrole <ID rôle>",
                "+gyend <ID>",
                "+gyrestart <ID>"
            ],
            "Bienvenue": [
                "+setwelcome <message>",
                "+setwelcomechannel <#salon>"
            ],
            "Règlement": [
                "+reglement <titre> <texte> <role> <image ou 'aucun'> <emoji ou 'aucun'> <texte bouton>"
            ],
            "Fun": [
                "+papa"
            ],
            "Snipe": [
                "+snipe"
            ]
        }

        embed = discord.Embed(title="Commandes disponibles", color=COLOR)
        if page:
            # Page spécifique
            page_name = page.capitalize()
            if page_name in pages:
                embed.add_field(name=page_name, value="\n".join(pages[page_name]), inline=False)
            else:
                embed.description = "Cette catégorie n'existe pas."
        else:
            # Toutes les pages
            for name, cmds in pages.items():
                embed.add_field(name=name, value="\n".join(cmds), inline=False)
        await ctx.author.send(embed=embed)
        await ctx.send("Je t'ai envoyé la liste de commandes en MP !")

def setup(bot):
    bot.add_cog(Aide(bot))
