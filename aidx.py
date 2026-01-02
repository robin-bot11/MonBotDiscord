from discord.ext import commands
import discord

OWNER_ID = 1383790178522370058

# ---------------- Catégories -> Cogs réels ----------------
CATEGORY_COGS = {
    "Modération": ["Moderation", "Modération"],
    "Logs": ["Logx"],
    "Giveaway": ["Givax"],
    "Fun": ["Funx", "Aidx", "Charlie3", "Bécassine"],
    "Bienvenue": ["JoinBot"],
    "Partenariat": ["Partenariat"],
    "Règlement": ["Policy"],
    "Vérification": ["Snipe"],
    "Owner": ["Creator"]
}

CATEGORY_COLORS = {
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

# ---------------- Select ----------------
class HelpSelect(discord.ui.Select):
    def __init__(self, bot, is_owner):
        self.bot = bot
        self.is_owner = is_owner

        options = [
            discord.SelectOption(label=cat)
            for cat in CATEGORY_COGS
            if cat != "Owner" or is_owner
        ]

        super().__init__(
            placeholder="📂 Choisis une catégorie",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]

        if category == "Owner" and interaction.user.id != OWNER_ID:
            return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)

        embed = discord.Embed(
            title=f"📂 {category}",
            color=CATEGORY_COLORS.get(category, 0x6b00cb)
        )

        found = False
        allowed_cogs = CATEGORY_COGS[category]

        for command in self.bot.commands:
            if command.hidden:
                continue

            if command.cog_name in allowed_cogs:
                embed.add_field(
                    name=f"+{command.name}",
                    value=command.help or "Pas de description",
                    inline=False
                )
                found = True

        if not found:
            embed.description = "Aucune commande trouvée pour cette catégorie."

        view = HelpView(self.bot, self.is_owner)
        await interaction.response.edit_message(embed=embed, view=view)

# ---------------- View ----------------
class HelpView(discord.ui.View):
    def __init__(self, bot, is_owner):
        super().__init__(timeout=None)
        self.add_item(HelpSelect(bot, is_owner))

# ---------------- Cog ----------------
class Aide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_cmd(self, ctx):
        embed = discord.Embed(
            title="[ + ] ROBIN • Aide",
            description=(
                "📘 Menu d’aide interactif\n\n"
                "➡️ Sélectionne une catégorie pour voir les commandes\n"
                "➡️ Préfixe : `+`"
            ),
            color=0x6b00cb
        )

        try:
            await ctx.author.send(
                embed=embed,
                view=HelpView(self.bot, ctx.author.id == OWNER_ID)
            )
            await ctx.reply("📬 Aide envoyée en MP.", mention_author=False)
        except discord.Forbidden:
            await ctx.reply("❌ Impossible de t’envoyer un MP.")

# ---------------- Setup ----------------
async def setup(bot):
    await bot.add_cog(Aide(bot))
