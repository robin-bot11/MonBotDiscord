import discord
from discord.ext import commands
from discord.ui import View, Button, Select

COLOR = 0x6b00cb

COMMANDS = {
    "Bienvenue / Vérification": [
        {"name": "+setupverify", "desc": "Configurer la vérification avec emoji"},
        {"name": "+setwelcome", "desc": "Configurer le welcome simple (texte)"},
        {"name": "+setwelcomeembed", "desc": "Configurer le welcome en embed"},
        {"name": "+togglewelcome", "desc": "Activer / désactiver le welcome sans supprimer la config"}
    ],
    "Fun": [
        {"name": "+papa", "desc": "Affiche un message fun pour le papa du serveur"}
    ],
    "Modération": [
        {"name": "+kick", "desc": "Expulse un membre du serveur"},
        {"name": "+ban", "desc": "Bannit un membre du serveur"},
        {"name": "+unban", "desc": "Débannit un utilisateur via son ID"},
        {"name": "+mute", "desc": "Mute un membre avec le rôle 'Muted'"},
        {"name": "+unmute", "desc": "Retire le rôle 'Muted' à un membre"},
        {"name": "+timeout", "desc": "Met un membre en timeout (minutes)"},
        {"name": "+giverole", "desc": "Donne un rôle à un membre"},
        {"name": "+takerole", "desc": "Retire un rôle à un membre"},
        {"name": "+warn", "desc": "Avertit un membre"},
        {"name": "+warns", "desc": "Affiche les warns d'un membre"},
        {"name": "+unwarn", "desc": "Supprime un warn spécifique"},
        {"name": "+purge", "desc": "Supprime un nombre spécifique de messages"},
        {"name": "+purgeall", "desc": "Supprime tous les messages du salon"}
    ],
    "Logs / Snipe": [
        {"name": "+snipe", "desc": "Affiche le dernier message supprimé"},
        {"name": "+editsnipe", "desc": "Affiche le dernier message édité"},
        {"name": "+logrole", "desc": "Logs de rôle"},
        {"name": "+logmod", "desc": "Logs modération"},
        {"name": "+logvoice", "desc": "Logs vocaux"},
        {"name": "+logchannel", "desc": "Logs de création/suppression/modification de salon"},
        {"name": "+logmessage", "desc": "Logs messages supprimés/édités"}
    ],
    "Owner": [
        {"name": "+ping", "desc": "Vérifie la latence du bot"},
        {"name": "+dm", "desc": "Envoie un message privé à un membre"},
        {"name": "+backupconfig", "desc": "Sauvegarde la configuration du bot"},
        {"name": "+restoreconfig", "desc": "Restaure la configuration depuis la sauvegarde"},
        {"name": "+resetwarns", "desc": "Réinitialise tous les warns d'un membre"},
        {"name": "+checkrole", "desc": "Vérifie un rôle spécifique"},
        {"name": "+checkchannel", "desc": "Vérifie un salon spécifique"},
        {"name": "+checkmember", "desc": "Vérifie un membre spécifique"},
        {"name": "+listbots", "desc": "Liste tous les bots du serveur"},
        {"name": "+servers", "desc": "Affiche les serveurs du bot"},
        {"name": "+invite", "desc": "Donne le lien d'invitation du bot"},
        {"name": "+shutdownbot", "desc": "Éteint le bot"},
        {"name": "+restartbot", "desc": "Redémarre le bot"},
        {"name": "+eval", "desc": "Exécute du code Python"}
    ]
}

# -------------------- EMBED GENERATOR --------------------
def generate_embed(category: str):
    cmds = COMMANDS.get(category, [])
    description = ""
    if not cmds:
        description = "Aucune commande trouvée pour cette catégorie."
    else:
        for cmd in cmds:
            description += f"**{cmd['name']}** — {cmd['desc']}\n"
    embed = discord.Embed(title=f"📂 {category}", description=description, color=COLOR)
    return embed

# -------------------- VIEW DASHBOARD --------------------
class HelpView(View):
    def __init__(self, user_id, owner_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.owner_id = owner_id

        # Menu déroulant
        self.add_item(HelpSelect(user_id, owner_id))

        # Barre de boutons
        for cat in ["Bienvenue / Vérification", "Fun", "Modération", "Logs / Snipe"]:
            self.add_item(CategoryButton(label=cat, user_id=user_id))

        if user_id == owner_id:
            self.add_item(CategoryButton(label="Owner", user_id=user_id))

        # Bouton Retour
        self.add_item(BackButton(user_id))

class HelpSelect(Select):
    def __init__(self, user_id, owner_id):
        options = [discord.SelectOption(label=cat) for cat in COMMANDS.keys() if cat != "Owner"]
        if user_id == owner_id:
            options.append(discord.SelectOption(label="Owner"))
        super().__init__(placeholder="Sélectionnez une catégorie", min_values=1, max_values=1, options=options)
        self.user_id = user_id
        self.owner_id = owner_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Ce menu n'est pas pour vous.", ephemeral=True)
        embed = generate_embed(self.values[0])
        await interaction.response.edit_message(embed=embed, view=self.view)

class CategoryButton(Button):
    def __init__(self, label, user_id):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=f"help_btn_{label}")
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Ce bouton n'est pas pour vous.", ephemeral=True)
        embed = generate_embed(self.label)
        await interaction.response.edit_message(embed=embed, view=self.view)

class BackButton(Button):
    def __init__(self, user_id):
        super().__init__(label="Retour", style=discord.ButtonStyle.secondary, custom_id="help_back_button")
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Ce bouton n'est pas pour vous.", ephemeral=True)
        embed = discord.Embed(
            title="📖 Menu d'aide",
            description=(
                "Bienvenue sur le menu d’aide du bot !\n"
                "Sélectionne une catégorie dans le menu ou la barre de boutons pour voir les commandes.\n"
                "Certaines commandes sont protégées et réservées au propriétaire."
            ),
            color=COLOR
        )
        await interaction.response.edit_message(embed=embed, view=self.view)

# -------------------- COG --------------------
class Help(commands.Cog):
    """Menu d'aide interactif style dashboard"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        owner_id = await self.bot.application_info()
        owner_id = owner_id.owner.id

        embed = discord.Embed(
            title="📖 Menu d'aide",
            description=(
                "Bienvenue sur le menu d’aide du bot !\n"
                "Sélectionne une catégorie dans le menu ou la barre de boutons pour voir les commandes.\n"
                "Certaines commandes sont protégées et réservées au propriétaire."
            ),
            color=COLOR
        )
        await ctx.send(embed=embed, view=HelpView(ctx.author.id, owner_id))

# -------------------- SETUP --------------------
async def setup(bot):
    await bot.add_cog(Help(bot))
