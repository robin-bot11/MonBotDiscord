from discord.ext import commands
import discord

COLOR = 0x6b00cb

# ---------------- CATEGORIES MANUELLES ----------------
COG_INFO = {
    "Moderation": {"emoji": "🛡"},
    "Fun": {"emoji": "🎉"},
    "Giveaway": {"emoji": "🎁"},
    "WelcomeVerification": {"emoji": "✉️"},
    "Message": {"emoji": "💬"},
    "Partenariat": {"emoji": "🤝"},
    "Reglement": {"emoji": "📜"},
    "Snipe": {"emoji": "👁️"},
}

HOME_TEXT = (
    "[ + ] 𝐑𝐨𝐛𝐢𝐍\n\n"
    "**Tu as fait +help ?**\n\n"
    "👁️ Chaque commande est présentée avec une description claire expliquant ce qu'elle fait.\n"
    "Certaines commandes sont réservées au propriétaire et n'apparaissent pas ici."
)

# ---------------- VIEW ----------------
class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot

    @discord.ui.select(
        placeholder="📂 Choisir une catégorie",
        options=[]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        cog_name = select.values[0]

        embed = discord.Embed(
            title=f"{COG_INFO.get(cog_name, {}).get('emoji', '')} {cog_name}",
            color=COLOR
        )

        # Commandes définies manuellement pour chaque cog
        commands_list = []

        if cog_name == "Moderation":
            commands_list = [
                ("ban", "Bannir un membre du serveur."),
                ("unban", "Débannir un membre."),
                ("mute", "Mettre un membre en silence."),
                ("unmute", "Retirer le mute d'un membre."),
            ]
        elif cog_name == "Fun":
            commands_list = [
                ("roll", "Lancer un dé."),
                ("coin", "Lancer une pièce."),
            ]
        elif cog_name == "Giveaway":
            commands_list = [
                ("gyveaway", "Lancer un giveaway."),
                ("gyrole", "Définir les rôles autorisés à lancer des giveaways."),
                ("gyend", "Terminer un giveaway avant l'heure."),
                ("gyrestart", "Relancer un giveaway terminé."),
            ]
        elif cog_name == "WelcomeVerification":
            commands_list = [
                ("setupverify", "Configurer la vérification avec emoji."),
                ("setwelcome", "Configurer le message de bienvenue texte."),
                ("setwelcomeembed", "Configurer le message de bienvenue en embed."),
                ("togglewelcome", "Activer ou désactiver le welcome."),
            ]
        elif cog_name == "Message":
            commands_list = [
                ("say", "Envoyer un message simple."),
                ("sayembed", "Envoyer un message en embed."),
                ("createchannel", "Créer un salon textuel ou vocal."),
                ("deletechannel", "Supprimer un salon textuel ou vocal."),
            ]
        elif cog_name == "Partenariat":
            commands_list = [
                ("setpartnerrole", "Configurer le rôle à ping lors d'un lien d'invitation."),
                ("setpartnerchannel", "Configurer le channel où détecter les invitations."),
            ]
        elif cog_name == "Reglement":
            commands_list = [
                ("reglement", "Configurer le règlement du serveur étape par étape."),
                ("showreglement", "Afficher le règlement avec bouton d'acceptation."),
            ]
        elif cog_name == "Snipe":
            commands_list = [
                ("snipe", "Afficher le dernier message supprimé."),
                ("editsnipe", "Afficher le dernier message édité."),
            ]

        if not commands_list:
            embed.description = "⚠️ Pas de commandes disponibles pour ce cog."
        else:
            for name, desc in commands_list:
                embed.add_field(name=f"+{name}", value=desc, inline=False)

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🏠 Accueil", style=discord.ButtonStyle.secondary)
    async def home(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="[ + ] 𝐑𝐨𝐛𝐢𝐍",
            description=HOME_TEXT,
            color=COLOR
        )
        await interaction.response.edit_message(embed=embed, view=self)

# ---------------- COG ----------------
class Help(commands.Cog):
    """Help interactif complet et fiable"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="[ + ] 𝐑𝐨𝐛𝐢𝐍",
            description=HOME_TEXT,
            color=COLOR
        )

        view = HelpView(self.bot)

        # Menu déroulant manuel avec toutes les catégories
        options = []
        for cog_name, info in COG_INFO.items():
            if cog_name in ["Moderation","Fun","Giveaway","WelcomeVerification","Message","Partenariat","Reglement","Snipe"]:
                description = "Commandes disponibles" if cog_name not in ["Message","Partenariat","Reglement"] else "⚠️ Pas de commandes disponibles" if cog_name in ["Message","Partenariat","Reglement"] else "Commandes disponibles"
                options.append(discord.SelectOption(
                    label=cog_name,
                    emoji=info["emoji"],
                    description=description
                ))

        view.select_callback.options = options
        await ctx.send(embed=embed, view=view)

# ---------------- SETUP ----------------
async def setup(bot):
    await bot.add_cog(Help(bot))
