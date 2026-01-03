import discord
from discord.ext import commands
from discord.ui import View, Select, Button

COLOR = 0x6b00cb

# ---------------- HELP DROPDOWN ----------------
class HelpDropdown(Select):
    def __init__(self, bot):
        self.bot = bot

        options = [
            discord.SelectOption(label="Modération", description="Commandes pour modérer le serveur"),
            discord.SelectOption(label="Giveaway", description="Commandes pour les giveaways"),
            discord.SelectOption(label="Welcome / Vérification", description="Configurations du welcome et vérification"),
            discord.SelectOption(label="Logs", description="Logs du serveur"),
            discord.SelectOption(label="MessageChannel", description="Gestion des salons/messages"),
            discord.SelectOption(label="Partenariat", description="Gestion des partenariats"),
            discord.SelectOption(label="Règlement", description="Gestion du règlement"),
            discord.SelectOption(label="Snipe", description="Affiche les messages supprimés"),
            discord.SelectOption(label="Fun", description="Commandes fun pour le serveur")
        ]

        super().__init__(placeholder="Sélectionnez une catégorie", min_values=1, max_values=1, options=options)

        # Commandes classées par catégorie + permissions
        self.cog_list = {
            "Modération": [
                "+kick <membre_id> [raison] — Expulse un membre (Mod/Admin)",
                "+ban <membre_id> [raison] — Bannit un membre (Mod/Admin)",
                "+unban <user_id> — Débannit un utilisateur (Mod/Admin)",
                "+mute <membre_id> [raison] — Mute un membre (Mod/Admin)",
                "+unmute <membre_id> — Unmute un membre (Mod/Admin)",
                "+timeout <membre_id> <minutes> — Timeout un membre (Max 28 jours) (Mod/Admin)",
                "+giverole <membre_id> <role_id> — Donne un rôle (Mod/Admin)",
                "+takerole <membre_id> <role_id> — Retire un rôle (Mod/Admin)",
                "+warn <membre_id> [raison] — Avertit un membre (Mod/Admin)",
                "+warns <membre_id> — Affiche les warns (Mod/Admin)",
                "+unwarn <membre_id> <num_warn> — Supprime un warn (Mod/Admin)",
                "+purge <nombre> — Supprime un nombre de messages (Mod/Admin)",
                "+purgeall — Supprime tous les messages du salon (Mod/Admin)"
            ],
            "Giveaway": [
                "+gyrole <@rôle> — Définir les rôles autorisés à lancer des giveaways (Admin)",
                "+gyveaway <durée> <gagnants> <récompense> — Lancer un giveaway (Admin)\n"
                "   Ex : +gyveaway 1j2h30m 3 Nitro",
                "+gyend <msg_id> — Terminer un giveaway actif (Admin)",
                "+gyvalidate <msg_id> — Valider manuellement un giveaway (Admin)\n"
                "   Affiche le gagnant, ping et DM automatiquement",
                "   Bouton “Relancer” disponible pour choisir un nouveau gagnant si activé"
            ],
            "Welcome / Vérification": [
                "+setupverify — Configurer la vérification par emoji (Admin)",
                "+setwelcome <#salon> <message> — Configurer le welcome texte (Admin)",
                "+setwelcomeembed <#salon> <titre> <description> [thumbnail] [image] — Configurer le welcome en embed (Admin)",
                "+togglewelcome — Activer / désactiver le welcome (Admin)"
            ],
            "Logs": [
                "+log_message #salon — Logs des messages supprimés ou édités",
                "+log_channel #salon — Logs de création/suppression/mise à jour des salons",
                "+log_vocal #salon — Logs des actions vocales (join/leave/move)",
                "+log_mod #salon — Logs de toutes les actions de modération (ban/kick/timeout/etc.)",
                "+log_role #salon — Logs des changements de rôles (ajout/retrait/création/suppression/mise à jour des permissions)",
                "+log_member #salon — Logs des modifications des membres (pseudo et rôles)"
            ],
            "MessageChannel": [
                "+say <message> — Envoyer un message simple (Admin)",
                "+sayembed <message> — Envoyer un message en embed (Admin)",
                "+createchannel <nom> [text/voice] — Créer un salon (Admin)",
                "+deletechannel <salon> — Supprimer un salon (Admin)"
            ],
            "Partenariat": [
                "+setpartnerrole <rôle> — Configure le rôle partenaire (Owner uniquement)",
                "+setpartnerchannel <#salon> — Configure le channel partenaire (Owner uniquement)"
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
        embed = discord.Embed(
            title=f"{cog_name}",
            description="\n".join(commands_list),
            color=COLOR
        )

        # Ajoute le bouton "Accueil"
        view = HomeButtonView(self.bot)
        view.add_item(self)
        await interaction.response.edit_message(embed=embed, view=view)

# ---------------- BOUTON ACCUEIL ----------------
class HomeButtonView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Accueil", style=discord.ButtonStyle.primary)
    async def home_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="💜 Menu d'aide",
            description="[ + ] 𝐑𝐨𝐛𝐢𝐧\n\n**Tu as fait +help ?**\n\nUtilise le menu de sélection ci-dessous pour choisir une catégorie.\nLes permissions requises sont indiquées pour chaque commande.",
            color=COLOR
        )
        await interaction.response.edit_message(embed=embed, view=HelpView(self.bot))

# ---------------- HELP VIEW ----------------
class HelpView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(HelpDropdown(bot))

# ---------------- HELP COMMAND ----------------
class HelpCommand(commands.Cog):
    """Help manuel pour tous les cogs"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        """Afficher le menu d'aide"""
        embed = discord.Embed(
            title="💜 Menu d'aide",
            description="[ + ] 𝐑𝐨𝐛𝐢𝐧\n\n**Tu as fait +help ?**\n\nUtilise le menu de sélection ci-dessous pour choisir une catégorie.\nLes permissions requises sont indiquées pour chaque commande.",
            color=COLOR
        )
        await ctx.send(embed=embed, view=HelpView(self.bot))

# ---------------- SETUP ----------------
async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
