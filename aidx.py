# help.py
import discord
from discord.ext import commands
from discord.ui import View, Select

COLOR = 0x6b00cb

class HelpDropdown(Select):
    def __init__(self, bot):
        self.bot = bot

        options = [
            discord.SelectOption(label="Modération", description="Commandes pour modérer le serveur"),
            discord.SelectOption(label="Giveaway", description="Commandes pour les giveaways"),
            discord.SelectOption(label="Welcome / Verification", description="Configurations du welcome et verification"),
            discord.SelectOption(label="Logs", description="Logs du serveur"),
            discord.SelectOption(label="MessageChannel", description="Gestion des salons/messages"),
            discord.SelectOption(label="Partenariat", description="Gestion du partenariat"),
            discord.SelectOption(label="Règlement", description="Gestion du règlement"),
            discord.SelectOption(label="Snipe", description="Affiche les messages supprimés"),
            discord.SelectOption(label="Fun", description="Commandes fun pour le serveur")
        ]

        super().__init__(placeholder="Sélectionnez une catégorie", min_values=1, max_values=1, options=options)

        # Commandes classées par catégorie + permissions
        self.cog_list = {
            "Modération": [
                "+kick <member_id> [raison] — Expulse un membre (Mod/Admin)",
                "+ban <member_id> [raison] — Bannit un membre (Mod/Admin)",
                "+unban <user_id> — Débannit un utilisateur (Mod/Admin)",
                "+mute <member_id> [raison] — Mute un membre (Mod/Admin)",
                "+unmute <member_id> — Unmute un membre (Mod/Admin)",
                "+timeout <member_id> <minutes> — Timeout un membre (Max 28 jours) (Mod/Admin)",
                "+giverole <member_id> <role_id> — Donne un rôle (Mod/Admin)",
                "+takerole <member_id> <role_id> — Retire un rôle (Mod/Admin)",
                "+warn <member_id> [raison] — Avertit un membre (Mod/Admin)",
                "+warns <member_id> — Affiche les warns (Mod/Admin)",
                "+unwarn <member_id> <num_warn> — Supprime un warn (Mod/Admin)",
                "+purge <amount> — Supprime un nombre de messages (Mod/Admin)",
                "+purgeall — Supprime tous les messages du salon (Mod/Admin)"
            ],
            "Giveaway": [
                "+gyrole <role> — Définir les rôles autorisés à lancer des giveaways (Admin)",
                "+gyveaway <durée> <récompense> — Lancer un giveaway (Admin)",
                "+gyend <msg_id> — Terminer un giveaway actif (Admin)",
                "+gyrestart <msg_id> — Relancer un giveaway actif (Admin)"
            ],
            "Welcome / Verification": [
                "+setupverify — Configurer la vérification par emoji (Admin)",
                "+setwelcome <#salon> <message> — Configurer le welcome texte (Admin)",
                "+setwelcomeembed <#salon> <title> <description> [thumbnail] [image] — Configurer le welcome en embed (Admin)",
                "+togglewelcome — Activer / désactiver le welcome (Admin)"
            ],
            "Logs": ["⚠️ Pas de commandes disponibles pour ce cog."],
            "MessageChannel": [
                "+say <message> — Envoyer un message simple (Admin)",
                "+sayembed <message> — Envoyer un message en embed (Admin)",
                "+createchannel <nom> [text/voice] — Créer un salon (Admin)",
                "+deletechannel <salon> — Supprimer un salon (Admin)"
            ],
            "Partenariat": [
                "+setpartnerrole <role> — Configure le rôle partenaire (Propriétaire uniquement)",
                "+setpartnerchannel <#salon> — Configure le channel partenaire (Propriétaire uniquement)"
            ],
            "Règlement": [
                "+reglement — Configurer le règlement étape par étape (Admin)",
                "+showreglement — Affiche le règlement avec le bouton d'acceptation"
            ],
            "Snipe": [
                "+snipe — Affiche le dernier message supprimé",
                "+purge_snipes_global — Supprime tous les snipes (Owner uniquement)",
                "+purge_snipes_guild — Supprime tous les snipes du serveur (Owner uniquement)"
            ],
            "Fun": [
                "+papa — Envoie un compliment aléatoire pour papa / 𝐃𝐄𝐔𝐒"
            ]
        }

    async def callback(self, interaction: discord.Interaction):
        cog_name = self.values[0]
        commands_list = self.cog_list.get(cog_name, ["⚠️ Pas de commandes disponibles pour ce cog."])
        embed = discord.Embed(title=f"{cog_name}", description="\n".join(commands_list), color=COLOR)
        await interaction.response.edit_message(embed=embed, view=self.view)

class HelpView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(HelpDropdown(bot))

class HelpCommand(commands.Cog):
    """Help manuel pour tous les cogs"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        """Afficher le menu d'aide"""
        embed = discord.Embed(
            title="Menu d'aide",
            description="Sélectionnez une catégorie ci-dessous :\n\nLes permissions requises sont indiquées pour chaque commande.",
            color=COLOR
        )
        await ctx.send(embed=embed, view=HelpView(self.bot))

# ------------------ Setup ------------------
async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
