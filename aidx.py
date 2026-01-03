from discord.ext import commands
import discord

COLOR = 0x6b00cb

COG_INFO = {
    "Moderation": {"emoji": "🔨", "priority": 1},
    "Logx": {"emoji": "📜", "priority": 2},
    "MessageChannel": {"emoji": "✉️", "priority": 3},
    "Snipe": {"emoji": "🔍", "priority": 4},
}

HOME_TEXT = (
    "💜 **Bienvenue dans le menu d'aide de MonBotDiscord !**\n\n"
    "Voici un aperçu de ce que chaque catégorie propose.\n\n"
    "**Moderation** : `+warn {user} {raison}` | `+kick {user}`\n"
    "**Message** : `+setwelcome {channel} {message}`\n"
    "**Snipe** : `+snipe`\n"
    "**Logs** : configuration automatique\n\n"
    "📌 Utilise le menu ci-dessous pour choisir une catégorie."
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
        cog = self.bot.get_cog(cog_name)

        embed = discord.Embed(
            title=f"{COG_INFO[cog_name]['emoji']} {cog_name}",
            color=COLOR
        )

        for cmd in cog.get_commands():
            desc = cmd.help or "Pas de description"
            embed.add_field(
                name=f"+{cmd.name}",
                value=f"{desc}\n**Exemple :** `{cmd.usage or 'Aucun exemple'}`",
                inline=False
            )

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🏠 Accueil", style=discord.ButtonStyle.secondary)
    async def home(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="💜 Aide de MonBotDiscord",
            description=HOME_TEXT,
            color=COLOR
        )
        await interaction.response.edit_message(embed=embed, view=self)

# ---------------- COG ----------------
class Help(commands.Cog):
    """Help interactif avec menu, accueil et exemples"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="💜 Aide de MonBotDiscord",
            description=HOME_TEXT,
            color=COLOR
        )

        view = HelpView(self.bot)

        # Génération dynamique du menu
        options = []
        for cog_name in sorted(COG_INFO, key=lambda x: COG_INFO[x]["priority"]):
            cog = self.bot.get_cog(cog_name)
            if cog:
                options.append(
                    discord.SelectOption(
                        label=cog_name,
                        emoji=COG_INFO[cog_name]["emoji"],
                        description=f"Commandes {cog_name}"
                    )
                )

        view.select_callback.options = options
        await ctx.send(embed=embed, view=view)

# ---------------- SETUP ----------------
async def setup(bot):
    await bot.add_cog(Help(bot))
