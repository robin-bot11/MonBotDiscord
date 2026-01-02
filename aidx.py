from discord.ext import commands
import discord

OWNER_ID = 1383790178522370058

# ---------------- Couleurs par catégorie ----------------
CATEGORY_STYLES = {
    "Modération": 0xE74C3C,
    "Logs": 0xF1C40F,
    "Giveaway": 0x1ABC9C,
    "Fun": 0x9B59B6,
    "Bienvenue": 0x3498DB,
    "Partenariat": 0xE67E22,
    "Règlement": 0x95A5A6,
    "Vérification": 0x2ECC71,
    "Owner": 0x6b00cb
}

# ---------------- Mapping catégorie -> Cogs ----------------
CATEGORY_COGS = {
    "Modération": ["Modération"],
    "Logs": ["Logx"],
    "Giveaway": ["Givax"],
    "Fun": ["FunX", "Aidx", "Charlie3", "Bécassine"],
    "Bienvenue": ["JoinBot"],
    "Partenariat": ["Partenariat"],
    "Règlement": ["Policy"],
    "Vérification": ["Snipe"],
    "Owner": ["Creator"]
}

# ---------------- Exemples + conseils ----------------
COMMAND_DETAILS = {
    "kick": {"example": "+kick <ID> Spam", "tip": "Expulse un membre.", "shortcut": "Peut utiliser +timeout pour mute temporaire.", "notes": "Ne peut pas expulser les membres supérieurs au bot."},
    "ban": {"example": "+ban <ID> Raid", "tip": "Bannit un membre.", "shortcut": "Combine avec +eval pour automatisation.", "notes": "Vérifie les permissions avant de ban."},
    "setstatus": {"example": "+setstatus en ligne | Jouant à Discord", "tip": "Change le statut du bot.", "shortcut": "Format : <state> | <activity>.", "notes": "Statuts : en ligne, hors ligne, invisible, occupé."},
    "shutdownbot": {"example": "+shutdownbot", "tip": "Éteint le bot.", "shortcut": "Utiliser si accès au déploiement.", "notes": "Commande irréversible, demande confirmation."}
    # Ajoute toutes tes commandes ici
}

# ---------------- Bouton pour mini-embed commande ----------------
class CommandDetailButton(discord.ui.Button):
    def __init__(self, cmd_name):
        super().__init__(label=f"{cmd_name}", style=discord.ButtonStyle.blurple)
        self.cmd_name = cmd_name

    async def callback(self, interaction: discord.Interaction):
        details = COMMAND_DETAILS.get(self.cmd_name)
        if not details:
            await interaction.response.send_message("Pas de détails disponibles.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Commande : {self.cmd_name}", color=0x6b00cb)
        embed.add_field(name="Exemple", value=f"`{details['example']}`", inline=False)
        embed.add_field(name="Conseil", value=details['tip'], inline=False)
        embed.add_field(name="Raccourci", value=details['shortcut'], inline=False)
        embed.add_field(name="Notes", value=details['notes'], inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ---------------- Bouton Retour ----------------
class BackButton(discord.ui.Button):
    def __init__(self, bot, is_owner):
        super().__init__(label="⬅️ Retour au menu", style=discord.ButtonStyle.gray)
        self.bot = bot
        self.is_owner = is_owner

    async def callback(self, interaction: discord.Interaction):
        view = HelpView(self.bot, self.is_owner)
        embed = discord.Embed(title="📜 Menu Aide", description="Sélectionne une catégorie :", color=0x6b00cb)
        await interaction.response.edit_message(embed=embed, view=view)

# ---------------- Menu déroulant catégorie ----------------
class HelpSelect(discord.ui.Select):
    def __init__(self, categories, is_owner: bool, bot):
        self.bot = bot
        self.is_owner = is_owner
        options = [discord.SelectOption(label=cat) for cat in categories]
        if is_owner and "Owner" not in [o.label for o in options]:
            options.append(discord.SelectOption(label="Owner"))
        super().__init__(placeholder="Sélectionne une catégorie", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        if category == "Owner" and interaction.user.id != OWNER_ID:
            return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)

        embed = discord.Embed(title=f"**{category}**", color=CATEGORY_STYLES.get(category, 0x6b00cb))
        view = discord.ui.View(timeout=None)
        found = False

        for cog_name in CATEGORY_COGS.get(category, []):
            cog = self.bot.get_cog(cog_name)
            if not cog:
                continue
            for cmd in cog.get_commands():
                if not cmd.hidden:
                    tip = COMMAND_DETAILS.get(cmd.name, {}).get("tip", "Pas de description")
                    embed.add_field(name=cmd.name, value=tip, inline=False)
                    view.add_item(CommandDetailButton(cmd.name))
                    found = True

        if not found:
            embed.description = "Aucune commande trouvée pour cette catégorie."

        # Ajout du bouton retour
        view.add_item(BackButton(self.bot, self.is_owner))
        await interaction.response.edit_message(embed=embed, view=view)

# ---------------- Vue interactive ----------------
class HelpView(discord.ui.View):
    def __init__(self, bot, is_owner: bool):
        super().__init__(timeout=None)
        self.bot = bot
        categories = [
            "Modération", "Logs", "Giveaway", "Fun",
            "Bienvenue", "Partenariat", "Règlement", "Vérification"
        ]
        self.add_item(HelpSelect(categories, is_owner, bot))

# ---------------- Commande +help ----------------
class AidePro(commands.Cog):
    """+help hyper-pro avec mini-embeds et navigation"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(title="📜 Menu Aide", description="Sélectionne une catégorie :", color=0x6b00cb)
        try:
            await ctx.author.send(embed=embed, view=HelpView(self.bot, ctx.author.id == OWNER_ID))
            await ctx.reply("📬 Aide envoyée en MP.", mention_author=False)
        except discord.Forbidden:
            await ctx.reply("❌ Impossible de t’envoyer un MP.", mention_author=False)

# ---------------- Setup ----------------
async def setup(bot):
    await bot.add_cog(AidePro(bot))
