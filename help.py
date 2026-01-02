# help_module.py
from discord.ext import commands
import discord

COLOR = 0x6b00cb
OWNER_ID = 1383790178522370058

# ---------------- Menu déroulant ----------------
class HelpSelect(discord.ui.Select):
    def __init__(self, is_owner: bool):
        options = [
            discord.SelectOption(label="Modération", emoji="🛡️"),
            discord.SelectOption(label="Giveaway", emoji="🎉"),
            discord.SelectOption(label="Fun", emoji="😂"),
            discord.SelectOption(label="Bienvenue", emoji="👋"),
            discord.SelectOption(label="Partenariat", emoji="🤝"),
            discord.SelectOption(label="Règlement", emoji="📜"),
        ]
        if is_owner:
            options.append(discord.SelectOption(label="Owner", emoji="👑"))

        super().__init__(
            placeholder="📖 Choisis une catégorie",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        embed = discord.Embed(color=COLOR)

        # ---------------- Modération ----------------
        if category == "Modération":
            embed.title = "🛡️ Modération"
            embed.description = (
                "**+kick `<ID> <raison>`**\n↳ Permission : Kick Members\n"
                "↳ Expulse temporairement un membre du serveur.\n\n"

                "**+ban `<ID> <raison>`**\n↳ Permission : Ban Members\n"
                "↳ Banni définitivement un membre du serveur.\n\n"

                "**+uban `<ID>`**\n↳ Permission : Ban Members\n"
                "↳ Retire un ban sur un membre.\n\n"

                "**+mute `<ID> <raison>`**\n↳ Permission : Manage Roles\n"
                "↳ Rend un membre muet, il ne pourra plus envoyer de messages.\n\n"

                "**+unmute `<ID>`**\n↳ Permission : Manage Roles\n"
                "↳ Retire le mute d'un membre.\n\n"

                "**+warn `<ID> <raison>`**\n↳ Permission : Manage Messages\n"
                "↳ Donne un avertissement à un membre.\n\n"

                "**+unwarn `<ID> <num>`**\n↳ Permission : Manage Messages\n"
                "↳ Supprime un avertissement spécifique d'un membre.\n\n"

                "**+warns `<ID>`**\n↳ Permission : Manage Messages\n"
                "↳ Affiche tous les avertissements d'un membre.\n\n"

                "**+purge `<nombre>`**\n↳ Permission : Manage Messages\n"
                "↳ Supprime un nombre précis de messages dans le salon.\n\n"

                "**+purgeall**\n↳ Permission : Administrateur\n"
                "↳ Supprime tous les messages du salon."
            )

        # ---------------- Giveaway ----------------
        elif category == "Giveaway":
            embed.title = "🎉 Giveaway"
            embed.description = (
                "**+gyveaway `<durée> <récompense>`**\n↳ Permission : Rôle autorisé\n"
                "↳ Lance un giveaway avec une durée et une récompense définie.\n\n"

                "**+gyrole `<@rôle>`**\n↳ Permission : Administrateur\n"
                "↳ Définit les rôles autorisés à lancer des giveaways.\n\n"

                "**+gyend `<ID>`**\n↳ Permission : Rôle autorisé\n"
                "↳ Termine un giveaway avant la fin.\n\n"

                "**+gyrestart `<ID>`**\n↳ Permission : Rôle autorisé\n"
                "↳ Relance un giveaway terminé."
            )

        # ---------------- Fun ----------------
        elif category == "Fun":
            embed.title = "😂 Fun"
            embed.description = (
                "**+papa**\n↳ Permission : Aucune\n"
                "↳ Réponse amusante ou blague fun (custom selon ton bot)."
            )

        # ---------------- Bienvenue ----------------
        elif category == "Bienvenue":
            embed.title = "👋 Bienvenue"
            embed.description = (
                "**+setwelcome `<message>`**\n↳ Permission : Administrateur\n"
                "↳ Configure le message de bienvenue. Utilise `{user}`, `{server}`, `{members}`.\n\n"

                "**+setwelcomechannel `<#channel>`**\n↳ Permission : Administrateur\n"
                "↳ Définit le salon où le message de bienvenue sera envoyé."
            )

        # ---------------- Partenariat ----------------
        elif category == "Partenariat":
            embed.title = "🤝 Partenariat"
            embed.description = (
                "**+setpartnerrole `<@rôle>`**\n↳ Permission : Owner\n"
                "↳ Définit le rôle à ping pour le salon partenariat.\n\n"

                "**+setpartnersalon `<#channel>`**\n↳ Permission : Owner\n"
                "↳ Définit le salon où les liens de partenariat seront envoyés automatiquement."
            )

        # ---------------- Règlement ----------------
        elif category == "Règlement":
            embed.title = "📜 Règlement"
            embed.description = (
                "**+reglement**\n↳ Permission : Administrateur\n"
                "↳ Lance un assistant interactif pour configurer le règlement :\n"
                "   • Titre\n"
                "   • Texte complet\n"
                "   • Rôle à donner après acceptation (ou `n` pour aucun)\n"
                "   • Texte du bouton\n"
                "   • Emoji (ou `n` pour aucun)\n"
                "   • Image (ou `n` pour aucune)\n\n"

                "**+showreglement**\n↳ Permission : Tous\n"
                "↳ Affiche le règlement avec le bouton d'acceptation."
            )

        # ---------------- Owner ----------------
        elif category == "Owner":
            if interaction.user.id != OWNER_ID:
                return await interaction.response.send_message(
                    "⛔ Accès refusé.",
                    ephemeral=True
                )
            embed.title = "👑 Owner"
            embed.description = (
                "**+ping**\n↳ Permission : Owner\n"
                "↳ Vérifie la latence du bot.\n\n"

                "**+dm `<ID> <message>`**\n↳ Permission : Owner\n"
                "↳ Envoie un message privé à un membre spécifique.\n\n"

                "**+backupconfig**\n↳ Permission : Owner\n"
                "↳ Sauvegarde la configuration et la base de données.\n\n"

                "**+restoreconfig**\n↳ Permission : Owner\n"
                "↳ Restaure la configuration et la base de données depuis la sauvegarde."
            )

        await interaction.response.edit_message(embed=embed, view=self.view)


# ---------------- Vue pour le menu ----------------
class HelpView(discord.ui.View):
    def __init__(self, is_owner: bool):
        super().__init__(timeout=180)
        self.add_item(HelpSelect(is_owner))


# ---------------- Commande Help ----------------
class Aide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        is_owner = ctx.author.id == OWNER_ID
        embed = discord.Embed(
            title="📖 Aide du bot",
            description="Utilise le menu déroulant pour afficher les commandes par catégorie.",
            color=COLOR
        )
        try:
            await ctx.author.send(embed=embed, view=HelpView(is_owner))
            await ctx.reply("📬 **Help envoyé en message privé.**", mention_author=False)
        except discord.Forbidden:
            await ctx.reply("❌ Impossible de t’envoyer un MP.")


# ---------------- Setup ----------------
async def setup(bot):
    await bot.add_cog(Aide(bot))
