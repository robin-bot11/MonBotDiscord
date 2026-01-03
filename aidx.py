from discord.ext import commands
import discord

COLOR = 0x6b00cb

# ---------------- CATEGORIES ----------------
COG_INFO = {
    "Moderation": {"emoji": "🔨", "priority": 1},
    "Fun": {"emoji": "🎉", "priority": 2},
    "Giveaway": {"emoji": "🎁", "priority": 3},
    "Snipe": {"emoji": "👁️", "priority": 4},
    "Welcome": {"emoji": "✉️", "priority": 5},  # Welcome + Verification
    "Message": {"emoji": "💬", "priority": 6},
}

HOME_TEXT = (
    "[ + ] 𝐑𝐨𝐛𝐢𝐍\n\n"
    "**Tu as fait +help ?**\n\n"
    "Utilise le menu de sélection ci-dessous pour choisir une catégorie.\n\n"
    "🔎 Chaque commande est présentée avec :\n"
    "• une description claire\n"
    "• les variables {} à utiliser\n"
    "• un exemple concret\n\n"
    "Certaines commandes sont réservées au propriétaire"
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
        if not cog:
            await interaction.response.send_message("⚠️ Cog introuvable.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"{COG_INFO[cog_name]['emoji']} {cog_name}",
            color=COLOR
        )

        for cmd in cog.get_commands():
            if cmd.hidden or cmd.enabled is False:
                continue
            desc = cmd.help or "Pas de description"

            # ✅ Exemples concrets pour chaque catégorie
            if cog_name == "Snipe":
                example = f"+{cmd.name}"  # rien de spécial, pas les commandes owner
            elif cog_name == "Message":
                if cmd.name == "say":
                    example = "+say Bonjour tout le monde !"
                elif cmd.name == "sayembed":
                    example = "+sayembed Salut en embed"
                elif cmd.name == "createchannel":
                    example = "+createchannel salon-text text"
                elif cmd.name == "deletechannel":
                    example = "+deletechannel salon-text"
                else:
                    example = f"+{cmd.name}"
            elif cog_name == "Welcome":
                if cmd.name == "setwelcome":
                    example = "+setwelcome #général Bienvenue {user} !"
                elif cmd.name == "setwelcomeembed":
                    example = "+setwelcomeembed #général Titre Description https://thumb.jpg https://image.jpg"
                elif cmd.name == "setupverify":
                    example = "+setupverify"
                elif cmd.name == "togglewelcome":
                    example = "+togglewelcome"
                else:
                    example = f"+{cmd.name}"
            else:
                example = cmd.usage or f"+{cmd.name}"

            embed.add_field(
                name=f"+{cmd.name}",
                value=f"{desc}\n**Exemple :** `{example}`",
                inline=False
            )

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
    """Help interactif complet et sécurisé"""

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

        # Génération dynamique du menu déroulant avec toutes les cogs
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
