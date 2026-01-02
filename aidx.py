from discord.ext import commands
import discord

OWNER_ID = 1383790178522370058

# ---------------- Couleurs par catégorie ----------------
CATEGORY_STYLES = {
    "Modération": 0xE74C3C,      # Rouge vif
    "Logs": 0xF1C40F,            # Jaune
    "Giveaway": 0x1ABC9C,        # Turquoise
    "Fun": 0x9B59B6,             # Violet
    "Bienvenue": 0x3498DB,       # Bleu
    "Partenariat": 0xE67E22,     # Orange
    "Règlement": 0x95A5A6,       # Gris
    "Vérification": 0x2ECC71,    # Vert
    "Owner": 0x6b00cb            # Violet foncé
}

# ---------------- Templates d'exemples pour les commandes ----------------
EXAMPLES = {
    "kick": "+kick 123456789012345678 Spam",
    "ban": "+ban 123456789012345678 Raid",
    "uban": "+uban 123456789012345678",
    "mute": "+mute 123456789012345678 Trop de spam",
    "unmute": "+unmute 123456789012345678",
    "warn": "+warn 123456789012345678 Mauvais comportement",
    "unwarn": "+unwarn 123456789012345678 0",
    "warns": "+warns 123456789012345678",
    "resetwarns": "+resetwarns 123456789012345678",
    "purge": "+purge 10",
    "purgeall": "+purgeall",
    "timeout": "+timeout 123456789012345678 1h",
    "say": "+say Bonjour tout le monde !",
    "sayembed": "+sayembed Message en embed",
    "createchannel": "+createchannel salon-text text",
    "deletechannel": "+deletechannel #general",
    "setlog": "+setlog message #logs",
    "gyveaway": "+gyveaway 1h Nitro",
    "gyrole": "+gyrole @Organisateur",
    "gyend": "+gyend 987654321098765432",
    "gyrestart": "+gyrestart 987654321098765432",
    "setwelcome": "+setwelcome #welcome Bienvenue {user} !",
    "setwelcomeembed": "+setwelcomeembed #welcome Titre Description",
    "togglewelcome": "+togglewelcome",
    "setpartnerrole": "+setpartnerrole @Partner",
    "setpartnersalon": "+setpartnersalon #partenariat",
    "reglement": "+reglement",
    "showreglement": "+showreglement",
    "setupverify": "+setupverify",
    "ping": "+ping",
    "dm": "+dm 123456789012345678 Salut !",
    "backupconfig": "+backupconfig",
    "restoreconfig": "+restoreconfig",
    "shutdownbot": "+shutdownbot",
    "restartbot": "+restartbot",
    "poweron": "+poweron",
    "eval": "+eval print('Hello World')",
    "servers": "+servers 1",
    "invite": "+invite 123456789012345678",
    "listbots": "+listbots",
    "checkrole": "+checkrole 123456789012345678",
    "checkchannel": "+checkchannel 123456789012345678",
    "checkmember": "+checkmember 123456789012345678",
    "papa": "+papa"
}

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

        if category == "Owner" and interaction.user.id != OWNER_ID:
            return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)

        desc = ""
        for cog_name, cog in bot.cogs.items():
            if category.lower() in cog_name.lower() or (category == "Owner" and cog_name.lower() == "owner"):
                for cmd in cog.get_commands():
                    if not cmd.hidden:
                        example = EXAMPLES.get(cmd.name, f"+{cmd.name} {cmd.signature}")
                        desc += f"**{example}**\n↳ {cmd.help or 'Pas de description'}\n\n"

        if not desc:
            desc = "Aucune commande trouvée pour cette catégorie."

        embed.title = f"**{category.upper()}**"
        embed.description = desc
        await interaction.response.edit_message(embed=embed, view=self.view)

# ---------------- Vue interactive ----------------
class HelpView(discord.ui.View):
    def __init__(self, bot, is_owner: bool):
        super().__init__(timeout=None)
        self.bot = bot
        categories = [
            "Modération", "Logs", "Giveaway", "Fun",
            "Bienvenue", "Partenariat", "Règlement", "Vérification"
        ]
        self.add_item(HelpSelect(categories, is_owner))

# ---------------- Commande Help ----------------
class Aide(commands.Cog):
    """Commande +help ultime stylée"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="[ + ] 𝐑𝐨𝐛𝐢𝐧 - Aide Premium",
            description=(
                "Voici toutes mes commandes avec **exemples dynamiques** et couleurs par catégorie !\n"
                "Navigue par catégorie avec le menu ci-dessous.\n\n"
                "Exemples : `<ID>` = 123456789012345678, `<#salon>` = #general, `<@rôle>` = @Membre.\n\n"
                "**Préfixe : `+`**"
            ),
            color=0x6b00cb
        )
        try:
            await ctx.author.send(embed=embed, view=HelpView(self.bot, ctx.author.id == OWNER_ID))
            await ctx.reply("📬 Aide envoyée en message privé.", mention_author=False)
        except discord.Forbidden:
            await ctx.reply("❌ Impossible de t’envoyer un MP.")

# ---------------- Setup ----------------
async def setup(bot):
    await bot.add_cog(Aide(bot))
