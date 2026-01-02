import discord
from discord.ext import commands

EMBED_COLOR = 0x6b00cb

# 🔥 Mapping COG → Catégorie affichée
COG_CATEGORIES = {
    "Moderation": "📂 Modération",
    "Logs": "📂 Logs",
    "Giveaway": "📂 Giveaway",
    "Snipe": "📂 Snipe",
    "Policy": "📂 Règlement",
    "Partenariat": "📂 Partenariat",
    "WelcomeVerification": "📂 Bienvenue / Vérification",
    "Fun": "📂 Fun",
    "Owner": "📂 Owner"
}

# 📋 Commandes pré-remplies pour chaque cog
COG_COMMANDS = {
    "Moderation": [
        ("kick <member_id> [raison]", "Expulse un membre du serveur."),
        ("ban <member_id> [raison]", "Bannit un membre du serveur."),
        ("unban <user_id>", "Débannit un utilisateur via son ID."),
        ("mute <member_id> [raison]", "Mute un membre en lui donnant le rôle 'Muted'."),
        ("unmute <member_id>", "Retire le rôle 'Muted' à un membre."),
        ("timeout <member_id> <minutes>", "Met un membre en timeout (max 28 jours)."),
        ("giverole <member_id> <role_id>", "Donne un rôle à un membre."),
        ("takerole <member_id> <role_id>", "Retire un rôle à un membre."),
        ("warn <member_id> [raison]", "Avertit un membre et le stocke."),
        ("warns <member_id>", "Affiche les warns d’un membre."),
        ("unwarn <member_id> <num>", "Supprime un warn spécifique."),
        ("purge <amount>", "Supprime un nombre spécifique de messages."),
        ("purgeall", "Supprime tous les messages du salon.")
    ],
    "Logs": [
        ("Voir les logs", "Suivi des messages, rôles, modérations, vocaux, etc.")
    ],
    "Giveaway": [
        ("gyveaway", "Lance un giveaway."),
        ("gyrole <@role>", "Définit les rôles autorisés à lancer des giveaways."),
        ("gyend", "Termine un giveaway avant l’heure."),
        ("gyrestart", "Relance un giveaway terminé.")
    ],
    "Snipe": [
        ("snipe", "Affiche le dernier message supprimé dans le salon.")
    ],
    "Policy": [
        ("reglement", "Configure le règlement avec titre, texte, rôle, bouton et emoji."),
        ("showreglement", "Affiche le règlement avec le bouton d’acceptation.")
    ],
    "Partenariat": [
        ("setpartnerrole <@role>", "Configure le rôle à ping lors d’un lien d’invitation."),
        ("setpartnerchannel <#salon>", "Configure le salon où les liens d’invitation sont détectés.")
    ],
    "WelcomeVerification": [
        ("setwelcome <message>", "Configure le message de bienvenue."),
        ("setwelcomechannel <#salon>", "Configure le salon pour le message de bienvenue."),
        ("setverification <role>", "Configure le rôle à donner après vérification.")
    ],
    "Fun": [
        ("Voir les commandes fun", "Blagues, mini-jeux, interactions, etc.")
    ],
    "Owner": [
        ("shutdown", "Éteint le bot."),
        ("poweron", "Rallume le bot."),
        ("restart", "Redémarre le bot."),
        ("eval <code>", "Exécute du code Python directement."),
        ("purgeall", "Supprime tous les messages du salon (admin requis)."),
        ("say <texte>", "Fait parler le bot."),
        ("status <texte>", "Change le statut du bot."),
        ("setprefix <nouveau préfixe>", "Change le préfixe."),
        ("backupconfig", "Sauvegarde la config du bot."),
        ("restoreconfig", "Restaure la config depuis une sauvegarde.")
    ]
}

# -------------------- VUES --------------------
class CategoryView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot
        for cog_name, label in COG_CATEGORIES.items():
            self.add_item(CategoryButton(cog_name, label, bot))

class CategoryButton(discord.ui.Button):
    def __init__(self, cog_name, label, bot):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary,
            custom_id=f"help_{cog_name}"
        )
        self.cog_name = cog_name
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=COG_CATEGORIES.get(self.cog_name, self.cog_name),
            color=EMBED_COLOR
        )
        commands_list = COG_COMMANDS.get(self.cog_name, [])
        if not commands_list:
            embed.description = "Aucune commande trouvée pour cette catégorie."
        else:
            for cmd_name, cmd_desc in commands_list:
                embed.add_field(name=f"+{cmd_name}", value=cmd_desc, inline=False)

        view = BackView(self.bot)
        await interaction.response.edit_message(embed=embed, view=view)

class BackView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot

    @discord.ui.button(label="⬅️ Retour", style=discord.ButtonStyle.primary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📖 Menu d'aide",
            description="Sélectionne une catégorie ci-dessous",
            color=EMBED_COLOR
        )
        await interaction.response.edit_message(embed=embed, view=CategoryView(self.bot))

# -------------------- COG HELP --------------------
class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="📖 Menu d'aide",
            description="Sélectionne une catégorie ci-dessous",
            color=EMBED_COLOR
        )
        await ctx.send(embed=embed, view=CategoryView(self.bot))

# -------------------- SETUP --------------------
async def setup(bot):
    await bot.add_cog(Help(bot))
