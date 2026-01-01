# aide.py
from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Aide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx, page: str = None):
        """Affiche la liste des commandes par catégorie ou une catégorie spécifique"""

        # --- Définir les pages avec description ---
        pages = {
            "Modération": {
                "+kick <ID> <raison>": "Expulse un membre du serveur.",
                "+ban <ID> <raison>": "Bannit un membre du serveur.",
                "+uban <ID>": "Débannit un membre.",
                "+mute <ID> <raison>": "Mute un membre.",
                "+unmute <ID>": "Démute un membre.",
                "+warn <ID> <raison>": "Ajoute un avertissement à un membre.",
                "+unwarn <ID> <num_warn>": "Supprime un avertissement spécifique.",
                "+warns <ID>": "Liste les warns d’un membre.",
                "+purge <nombre>": "Supprime un nombre de messages dans le salon.",
                "+purgeall": "Supprime tous les messages du salon."
            },
            "Giveaway": {
                "+gyveaway <durée> <récompense>": "Lance un giveaway.",
                "+gyrole <ID rôle>": "Définit les rôles autorisés à lancer des giveaways.",
                "+gyend <ID>": "Termine un giveaway manuellement.",
                "+gyrestart <ID>": "Relance un giveaway actif."
            },
            "Messages / Salons": {
                "+say <texte>": "Faire parler le bot dans le salon.",
                "+sayembed <texte>": "Faire parler le bot avec un embed.",
                "+createchannel <nom> <type>": "Créer un salon textuel ou vocal.",
                "+deletechannel <#salon>": "Supprime un salon mentionné."
            },
            "Bienvenue": {
                "+setwelcome <message>": "Configure le message de bienvenue.",
                "+setwelcomechannel <#salon>": "Configure le salon où envoyer le message de bienvenue."
            },
            "Règlement": {
                "+reglement <titre> <texte> <role> <image ou 'aucun'> <emoji ou 'aucun'> <texte bouton>": "Configure le règlement du serveur."
            },
            "Fun": {
                "+papa": "Une commande fun pour célébrer le papa du serveur."
            },
            "Snipe": {
                "+snipe": "Récupère le dernier message supprimé dans un salon."
            }
        }

        embed = discord.Embed(title="Commandes disponibles", color=COLOR)

        # --- Affichage d'une page spécifique ---
        if page:
            page_name = page.capitalize()
            if page_name in pages:
                cmds = pages[page_name]
                value = "\n".join([f"{cmd} : {desc}" for cmd, desc in cmds.items()])
                embed.add_field(name=page_name, value=value, inline=False)
            else:
                embed.description = "Cette catégorie n'existe pas."
        else:
            # --- Affichage de toutes les catégories ---
            for category, cmds in pages.items():
                value = "\n".join([f"{cmd} : {desc}" for cmd, desc in cmds.items()])
                embed.add_field(name=category, value=value, inline=False)

        # --- Essayer d'envoyer en DM ---
        try:
            await ctx.author.send(embed=embed)
            await ctx.send("Je t'ai envoyé la liste de commandes en MP !")
        except discord.Forbidden:
            await ctx.send(f"{ctx.author.mention}, je n'ai pas pu t'envoyer les commandes en MP. Vérifie que tes DM sont ouverts.")

def setup(bot):
    bot.add_cog(Aide(bot))
