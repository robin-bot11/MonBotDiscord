# aide_pro_copy.py
from discord.ext import commands
import discord

OWNER_ID = 1383790178522370058

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

COMMANDS_INFO = {
    # Exemple pour toutes les catégories, à compléter
    "kick": {
        "syntax": "+kick <ID> [raison]",
        "example": "+kick 123456789012345678 Spam",
        "desc": "Expulse un membre du serveur.",
        "tips": "Vérifie que le membre n’est pas Admin ou supérieur."
    },
    "ping": {
        "syntax": "+ping",
        "example": "+ping",
        "desc": "Teste si le bot est en ligne.",
        "tips": "Utile pour vérifier la réactivité."
    },
    "setstatus": {
        "syntax": "+setstatus <online|idle|dnd|invisible> [activité]",
        "example": "+setstatus online Joueur en ligne",
        "desc": "Change le statut et activité du bot.",
        "tips": "Ex : 'Playing', 'Streaming', 'Listening'."
    },
    # Ajoute ici toutes tes autres commandes avec syntax, example, desc, tips
}

# ---------------- Select pour chaque commande ----------------
class CommandSelect(discord.ui.Select):
    def __init__(self, commands_list, category, parent_view):
        options = [
            discord.SelectOption(label=cmd, description=COMMANDS_INFO.get(cmd, {}).get("desc", "")[:50])
            for cmd in commands_list
        ]
        super().__init__(placeholder="Sélectionne une commande", min_values=1, max_values=1, options=options)
        self.category = category
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        cmd_name = self.values[0]
        info = COMMANDS_INFO.get(cmd_name, {})
        embed = discord.Embed(
            title=f"📌 {cmd_name} ({self.category})",
            description=info.get("desc", "Pas de description."),
            color=CATEGORY_STYLES.get(self.category, 0x6b00cb)
        )
        embed.add_field(name="Syntaxe", value=info.get("syntax", f"+{cmd_name} ..."), inline=False)
        embed.add_field(name="Exemple", value=info.get("example", ""), inline=False)
        embed.add_field(name="Conseils / Tips", value=info.get("tips", "—"), inline=False)

        # ---------------- Vue avec bouton retour + copier ----------------
        view = discord.ui.View()
        # Bouton retour
        btn_back = discord.ui.Button(label="🔙 Retour", style=discord.ButtonStyle.gray)
        async def back_callback(interaction2):
            await interaction2.response.edit_message(embed=self.parent_view.category_embed, view=self.parent_view)
        btn_back.callback = back_callback
        view.add_item(btn_back)

        # Bouton copier la commande
        btn_copy = discord.ui.Button(label="📋 Copier l'exemple", style=discord.ButtonStyle.green)
        async def copy_callback(interaction2):
            await interaction2.response.send_message(f"`{info.get('example', cmd_name)}`", ephemeral=True)
        btn_copy.callback = copy_callback
        view.add_item(btn_copy)

        await interaction.response.edit_message(embed=embed, view=view)

# ---------------- Vue catégorie ----------------
class CategoryView(discord.ui.View):
    def __init__(self, bot, category, commands_list):
        super().__init__(timeout=None)
        self.bot = bot
        self.category = category
        self.category_embed = discord.Embed(
            title=f"📂 {category}",
            description="Sélectionne une commande pour voir exemple, syntaxe et conseils.",
            color=CATEGORY_STYLES.get(category, 0x6b00cb)
        )
        self.add_item(CommandSelect(commands_list, category, self))

# ---------------- Select catégorie ----------------
class HelpSelect(discord.ui.Select):
    def __init__(self, categories, is_owner, bot):
        options = [discord.SelectOption(label=cat) for cat in categories]
        if is_owner and "Owner" not in [o.label for o in options]:
            options.append(discord.SelectOption(label="Owner"))
        super().__init__(placeholder="Sélectionne une catégorie", min_values=1, max_values=1, options=options)
        self.bot = bot
        self.is_owner = is_owner

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        if category == "Owner" and interaction.user.id != OWNER_ID:
            return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)

        commands_list = []
        for cog_name, cog in self.bot.cogs.items():
            if category.lower() in cog_name.lower() or (category == "Owner" and cog_name.lower() == "creator"):
                for cmd in cog.get_commands():
                    if not cmd.hidden:
                        commands_list.append(cmd.name)

        if not commands_list:
            return await interaction.response.send_message("Aucune commande trouvée.", ephemeral=True)

        view = CategoryView(self.bot, category, commands_list)
        await interaction.response.edit_message(embed=view.category_embed, view=view)

# ---------------- Vue principale ----------------
class HelpView(discord.ui.View):
    def __init__(self, bot, is_owner: bool):
        super().__init__(timeout=None)
        self.bot = bot
        categories = [
            "Modération", "Logs", "Giveaway", "Fun",
            "Bienvenue", "Partenariat", "Règlement", "Vérification"
        ]
        self.add_item(HelpSelect(categories, is_owner, bot))
        self.main_embed = discord.Embed(
            title="[ + ] 𝐑𝐨𝐛𝐢𝐧 - Aide Interactive",
            description="Sélectionne une catégorie pour voir toutes les commandes interactives.\nChaque commande peut être copiée grâce au bouton vert 📋.",
            color=0x6b00cb
        )

# ---------------- Cog +help ----------------
class AideProCopy(commands.Cog):
    """+help interactif Pro Max avec copier l'exemple"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        view = HelpView(self.bot, ctx.author.id == OWNER_ID)
        try:
            await ctx.author.send(embed=view.main_embed, view=view)
            await ctx.reply("📬 Aide envoyée en message privé.", mention_author=False)
        except discord.Forbidden:
            await ctx.reply("❌ Impossible de t’envoyer un MP.", mention_author=False)

# ---------------- Setup ----------------
async def setup(bot):
    await bot.add_cog(AideProCopy(bot))
