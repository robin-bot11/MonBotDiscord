# help.py
import discord
from discord.ext import commands
from discord.ui import View, Button, Select

COLOR = 0x6b00cb
OWNER_COGS = ["Creator"]

# ---------------- CATEGORIES ----------------
COG_CATEGORIES = {
    "Moderation": "Modération",
    "Fun": "Fun",
    "WelcomeVerification": "Bienvenue / Vérification",
    "Logx": "Logs",
    "Creator": "Owner"
}

# ----------------- SELECT -----------------
class HelpSelect(Select):
    def __init__(self, bot):
        options = [
            discord.SelectOption(label=display_name, value=cog_name)
            for cog_name, display_name in COG_CATEGORIES.items()
        ]
        super().__init__(placeholder="Sélectionnez une catégorie", min_values=1, max_values=1, options=options)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        cog_name = self.values[0]
        cog = self.bot.get_cog(cog_name)

        embed = discord.Embed(title=f"📂 {COG_CATEGORIES[cog_name]}", color=COLOR)

        if not cog:
            embed.description = "Aucune commande trouvée pour cette catégorie."
        else:
            cmds = cog.get_commands()
            desc = ""
            for cmd in cmds:
                if cmd.hidden:
                    continue
                cmd_desc = cmd.help or "Pas de description"
                if cog_name in OWNER_COGS:
                    cmd_desc += " — **Protégée / Owner**"
                desc += f"+{cmd.name} — {cmd_desc}\n"
            embed.description = desc or "Aucune commande trouvée pour cette catégorie."

        # Bouton retour
        view = View(timeout=None)
        view.add_item(Button(label="⬅️ Retour", style=discord.ButtonStyle.gray, custom_id="help_home"))
        view.add_item(self)  # garder le menu déroulant
        await interaction.response.edit_message(embed=embed, view=view)

# ----------------- VIEW -----------------
class HelpView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(HelpSelect(bot))

# ----------------- BUTTON RETOUR -----------------
class HelpHomeButton(Button):
    def __init__(self, bot):
        super().__init__(label="⬅️ Retour", style=discord.ButtonStyle.gray, custom_id="help_home")
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📖 Menu d'aide",
            description=(
                "Tu as fait +help ?\n\n"
                "Bienvenue sur le menu d’aide du bot !\n"
                "Sélectionne une catégorie dans le menu ci-dessous pour voir les commandes disponibles."
            ),
            color=COLOR
        )
        embed.set_footer(text="Certaines commandes sont protégées et réservées au propriétaire.")
        await interaction.response.edit_message(embed=embed, view=HelpView(self.bot))

# ----------------- COG -----------------
class Help(commands.Cog):
    """Menu d'aide interactif"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def show_help(self, ctx):
        embed = discord.Embed(
            title="📖 Menu d'aide",
            description=(
                "Tu as fait +help ?\n\n"
                "Bienvenue sur le menu d’aide du bot !\n"
                "Sélectionne une catégorie dans le menu ci-dessous pour voir les commandes disponibles."
            ),
            color=COLOR
        )
        embed.set_footer(text="Certaines commandes sont protégées et réservées au propriétaire.")
        await ctx.send(embed=embed, view=HelpView(self.bot))

# ----------------- SETUP -----------------
async def setup(bot):
    await bot.add_cog(Help(bot))
