from discord.ext import commands
import discord

COLOR = 0x6b00cb
OWNER_ID = 1383790178522370058

# ---------------- Menu déroulant ----------------
class HelpSelect(discord.ui.Select):
    def __init__(self, is_owner: bool):
        options = [
            discord.SelectOption(label="Modération"),
            discord.SelectOption(label="Logs"),
            discord.SelectOption(label="Giveaway"),
            discord.SelectOption(label="Fun"),
            discord.SelectOption(label="Bienvenue"),
            discord.SelectOption(label="Partenariat"),
            discord.SelectOption(label="Règlement"),
            discord.SelectOption(label="Vérification")  # publique
        ]
        if is_owner:
            options.append(discord.SelectOption(label="Owner"))

        super().__init__(
            placeholder="Sélectionne une catégorie",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        cat = self.values[0]
        embed = discord.Embed(color=COLOR)

        # ---------------- Modération ----------------
        if cat == "Modération":
            embed.title = "Modération"
            embed.description = (
                "**+kick `<ID> <raison>`**\n↳ Expulse temporairement un membre\n\n"
                "**+ban `<ID> <raison>`**\n↳ Banni définitivement un membre\n\n"
                "**+uban `<ID>`**\n↳ Retire un ban\n\n"
                "**+mute `<ID> <raison>`**\n↳ Rend un membre muet\n\n"
                "**+unmute `<ID>`**\n↳ Retire le mute\n\n"
                "**+warn `<ID> <raison>`**\n↳ Donne un avertissement\n\n"
                "**+unwarn `<ID> <num>`**\n↳ Supprime un avertissement spécifique\n\n"
                "**+warns `<ID>`**\n↳ Affiche tous les avertissements\n\n"
                "**+resetwarns `<ID>`**\n↳ Supprime tous les warns d'un membre\n\n"
                "**+purge `<nombre>`**\n↳ Supprime un nombre précis de messages\n\n"
                "**+purgeall**\n↳ Supprime tous les messages du salon\n\n"
                "**+timeout `<ID> <durée>`**\n↳ Timeout temporaire d’un membre (max 28 jours)"
            )

        # ---------------- Logs ----------------
        elif cat == "Logs":
            embed.title = "Logs"
            embed.description = (
                "**+setlog message `<#salon>`**\n↳ Logs messages\n\n"
                "**+setlog mod `<#salon>`**\n↳ Logs modération\n\n"
                "**+setlog channel `<#salon>`**\n↳ Logs salons\n\n"
                "**+setlog voice `<#salon>`**\n↳ Logs vocaux\n\n"
                "**+setlog member `<#salon>`**\n↳ Logs membres\n\n"
                "**+setlog role `<#salon>`**\n↳ Logs rôles"
            )

        # ---------------- Giveaway ----------------
        elif cat == "Giveaway":
            embed.title = "Giveaway"
            embed.description = (
                "**+gyveaway `<durée> <récompense>`**\n↳ Lance un giveaway\n\n"
                "**+gyrole `<@rôle>`**\n↳ Définit les rôles autorisés\n\n"
                "**+gyend `<ID>`**\n↳ Termine un giveaway\n\n"
                "**+gyrestart `<ID>`**\n↳ Relance un giveaway terminé"
            )

        # ---------------- Fun ----------------
        elif cat == "Fun":
            embed.title = "Fun"
            embed.description = "**+papa**\n↳ Réponse amusante ou blague fun"

        # ---------------- Bienvenue ----------------
        elif cat == "Bienvenue":
            embed.title = "Bienvenue"
            embed.description = (
                "**+setwelcome `<message>`**\n↳ Configure le message de bienvenue\n\n"
                "**+setwelcomechannel `<#channel>`**\n↳ Définit le salon pour le message de bienvenue"
            )

        # ---------------- Partenariat ----------------
        elif cat == "Partenariat":
            embed.title = "Partenariat"
            embed.description = (
                "**+setpartnerrole `<@rôle>`**\n↳ Définit le rôle à ping\n\n"
                "**+setpartnersalon `<#channel>`**\n↳ Définit le salon partenariat"
            )

        # ---------------- Règlement ----------------
        elif cat == "Règlement":
            embed.title = "Règlement"
            embed.description = (
                "**+reglement**\n↳ Lance l’assistant interactif pour configurer le règlement\n\n"
                "**+showreglement**\n↳ Affiche le règlement avec le bouton d’acceptation"
            )

        # ---------------- Vérification ----------------
        elif cat == "Vérification":
            embed.title = "Vérification"
            embed.description = (
                "**+setverifyrole `<@rôle>`**\n↳ Définit le rôle à donner après vérification\n\n"
                "**+setunverifiedrole `<@rôle>`**\n↳ Définit le rôle à retirer après vérification (optionnel)\n\n"
                "**+sendverify `<#salon>` `<titre>` <description>`**\n↳ Envoie l'embed interactif de vérification"
            )

        # ---------------- Owner ----------------
        elif cat == "Owner":
            if interaction.user.id != OWNER_ID:
                return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)
            embed.title = "Owner"
            embed.description = (
                "**+ping**\n↳ Vérifie la latence\n\n"
                "**+dm `<ID> <message>`**\n↳ Envoie un message privé\n\n"
                "**+backupconfig**\n↳ Sauvegarde la configuration\n\n"
                "**+restoreconfig**\n↳ Restaure la configuration\n\n"
                "**+shutdownbot**\n↳ Éteint le bot\n\n"
                "**+restartbot**\n↳ Redémarre le bot\n\n"
                "**+poweron**\n↳ Relance les services internes\n\n"
                "**+eval `<code>`**\n↳ Évalue du code Python\n\n"
                "**+servers `<page>`**\n↳ Liste les serveurs avec pagination\n\n"
                "**+invite `<ID serveur>`**\n↳ Envoie une invitation pour un serveur\n\n"
                "**+listbots**\n↳ Liste tous les bots sur le serveur\n\n"
                "**+checkrole `<ID>`**\n↳ Affiche les permissions d’un rôle\n\n"
                "**+checkchannel `<ID>`**\n↳ Affiche les infos d’un salon\n\n"
                "**+checkmember `<ID>`**\n↳ Affiche les rôles et permissions d’un membre\n\n"
                "**+resetwarns `<ID>`**\n↳ Supprime tous les warns d’un membre"
            )

        await interaction.response.edit_message(embed=embed, view=self.view)

# ---------------- Vue pour le menu (permanente) ----------------
class HelpView(discord.ui.View):
    def __init__(self, is_owner: bool):
        super().__init__(timeout=None)
        self.add_item(HelpSelect(is_owner))

# ---------------- Commande Help ----------------
class Aide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="[ + ] 𝐑𝐨𝐛𝐢𝐧",
            description=(
                "Tu as fait `+help` ?\n\n"
                "Tu es dans **la liste de mes commandes**, je vais te guider à travers toutes mes fonctionnalités.\n\n"
                "Tout est organisé par catégorie pour que tu puisses naviguer facilement.\n\n"
                "Certaines commandes nécessitent des autorisations spécifiques.\n"
                "Elles sont
