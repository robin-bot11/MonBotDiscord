from discord.ext import commands
import discord

COLOR = 0x6b00cb

# ---------------- CATEGORIES ----------------
COG_INFO = {
    "Moderation": {"emoji": "🛡", "priority": 1},
    "Fun": {"emoji": "🎉", "priority": 2},
    "Giveaway": {"emoji": "🎁", "priority": 3},
    "WelcomeVerification": {"emoji": "✉️", "priority": 4},
    "Message": {"emoji": "💬", "priority": 5},
    "Partenariat": {"emoji": "🤝", "priority": 6},
    "Reglement": {"emoji": "📜", "priority": 7},
    "Snipe": {"emoji": "👁️", "priority": 8},
}

HOME_TEXT = (
    "[ + ] 𝐑𝐨𝐛𝐢𝐍\n\n"
    "**Tu as fait +help ?**\n\n"
    "Utilise le menu de sélection ci-dessous pour choisir une catégorie.\n\n"
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
        cog = self.bot.get_cog(cog_name)

        # Embed de base
        embed = discord.Embed(
            title=f"{COG_INFO.get(cog_name, {}).get('emoji', '')} {cog_name}",
            color=COLOR
        )

        if not cog or not any(cmd for cmd in cog.get_commands() if not cmd.hidden and cmd.enabled and not getattr(cmd, "owner_only", False)):
            embed.description = "⚠️ Pas de commandes disponibles pour ce cog."
        else:
            for cmd in cog.get_commands():
                if cmd.hidden or not cmd.enabled or getattr(cmd, "owner_only", False):
                    continue
                # Description automatique si help non défini
                desc = cmd.help or f"Cette commande exécute `+{cmd.name}`."
                embed.add_field(name=f"+{cmd.name}", value=desc, inline=False)

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
    """Help interactif complet et professionnel"""

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

        # Génération dynamique du menu avec toutes les catégories
        options = []
        for cog_name in sorted(COG_INFO, key=lambda x: COG_INFO[x]["priority"]):
            cog = self.bot.get_cog(cog_name)
            has_cmds = any(cmd for cmd in cog.get_commands() if not cmd.hidden and cmd.enabled and not getattr(cmd, "owner_only", False)) if cog else False
            description = f"Commandes {cog_name}" if has_cmds else "Pas de commandes disponibles"
            options.append(
                discord.SelectOption(
                    label=cog_name,
                    emoji=COG_INFO[cog_name]["emoji"],
                    description=description,
                    default=False
                )
            )

        view.select_callback.options = options
        await ctx.send(embed=embed, view=view)

# ---------------- SETUP ----------------
async def setup(bot):
    await bot.add_cog(Help(bot))
