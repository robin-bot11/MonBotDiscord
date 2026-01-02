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

# ---------------- Mapping Catégories → Cogs ----------------
CATEGORY_COGS = {
    "Modération": ["modération"],
    "Logs": ["logx"],
    "Giveaway": ["givax"],
    "Fun": ["funx", "aidx", "charlie3", "bécassine"],
    "Bienvenue": ["joinbot"],
    "Partenariat": ["partenariat"],
    "Règlement": ["policy"],
    "Vérification": ["snipe"],
    "Owner": ["delta4"]
}

# ---------------- Exemples + conseils avancés ----------------
COMMAND_DETAILS = {
    "kick": {
        "example": "+kick <ID> Spam",
        "tip": "Expulse un membre du serveur.",
        "shortcut": "Tu peux aussi utiliser +timeout pour mute temporaire.",
        "notes": "Ne peut pas expulser les membres avec un rôle supérieur au bot."
    },
    "ban": {
        "example": "+ban <ID> Raid",
        "tip": "Bannit un membre.",
        "shortcut": "Peut combiner avec +eval pour automatisation avancée.",
        "notes": "Vérifie les permissions avant de ban."
    },
    "setstatus": {
        "example": "+setstatus en ligne | Jouant à Discord",
        "tip": "Change le statut du bot.",
        "shortcut": "Format : <state> | <activity>.",
        "notes": "Les statuts possibles : en ligne, hors ligne, invisible, occupé."
    },
    "shutdownbot": {
        "example": "+shutdownbot",
        "tip": "Éteint le bot.",
        "shortcut": "Utiliser seulement si tu as accès à Railway ou déploiement.",
        "notes": "Commande irréversible, demande confirmation."
    }
    # Ajoute toutes tes commandes ici
}

# ---------------- Bouton pour ouvrir mini embed ----------------
class CommandDetailButton(discord.ui.Button):
    def __init__(self, cmd_name):
        super().__init__(label=f"{cmd_name}", style=discord.ButtonStyle.blurple)
        self.cmd_name = cmd_name

    async def callback(self, interaction: discord.Interaction):
        details = COMMAND_DETAILS.get(self.cmd_name)
        if not details:
            await interaction.response.send_message("Pas de détails disponibles.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"Commande : {self.cmd_name}",
            color=0x6b00cb
        )
        embed.add_field(name="Exemple", value=f"`{details['example']}`", inline=False)
        embed.add_field(name="Conseil", value=details['tip'], inline=False)
        embed.add_field(name="Raccourci", value=details['shortcut'], inline=False)
        embed.add_field(name="Notes", value=details['notes'], inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

# ---------------- Menu déroulant ----------------
class HelpSelect(discord.ui.Select):
    def __init__(self, categories, is_owner: bool):
        options = [discord.SelectOption(label=cat) for cat in categories]
        if is_owner and "Owner" not in [o.label for o in options]:
            options.append(discord.SelectOption(label="Owner"))
        super().__init__(placeholder="Sélectionne une catégorie", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        bot = self.view.bot
        color = CATEGORY_STYLES.get(category, 0x6b00cb)
        embed = discord.Embed(color=color)
        embed.set_footer(text="Préfixe : +")
        view = discord.ui.View(timeout=None)

        if category == "Owner" and interaction.user.id != OWNER_ID:
            return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)

        found = False
        # ✅ Utilise le mapping catégorie → cogs
        cogs_for_category = CATEGORY_COGS.get(category, [])
        for cog_name in cogs_for_category:
            cog = bot.get_cog(cog_name)
            if not cog:
                continue
            for cmd in cog.get_commands():
                if not cmd.hidden:
                    embed.add_field(
                        name=cmd.name,
                        value=COMMAND_DETAILS.get(cmd.name, {}).get("tip", "Pas de description"),
                        inline=False
                    )
                    view.add_item(CommandDetailButton(cmd.name))
                    found = True

        if not found:
            embed.description = "Aucune commande trouvée pour cette catégorie."

        await interaction.response.edit_message(embed=embed, view=view)

# ---------------- Vue interactive ----------------
class HelpView(discord.ui.View):
    def __init__(self, bot, is_owner: bool):
        super().__init__(timeout=None)
        self.bot = bot
        categories = list(CATEGORY_STYLES.keys())
        self.add_item(HelpSelect(categories, is_owner))

# ---------------- Commande Help ----------------
class AidePro(commands.Cog):
    """+help hyper-pro avec mini-embeds détaillés"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="[ + ] 𝐑𝐨𝐛𝐢𝐧 - Aide Hyper-Pro",
            description=(
                "Toutes mes commandes avec **exemples dynamiques**, **tips**, **mini-embeds détaillés**.\n"
                "Navigue par catégorie avec le menu ci-dessous.\n\n"
                "Exemples : `<ID>` = 123456789012345678, `<#salon>` = #general, `<@rôle>` = @Membre.\n"
                "**Préfixe : `+`**"
            ),
            color=0x6b00cb
        )
        try:
            await ctx.author.send(embed=embed, view=HelpView(self.bot, ctx.author.id == OWNER_ID))
            await ctx.reply("📬 Aide envoyée en MP.", mention_author=False)
        except discord.Forbidden:
            await ctx.reply("❌ Impossible de t’envoyer un MP.", mention_author=False)

# ---------------- Setup ----------------
async def setup(bot):
    await bot.add_cog(AidePro(bot))
