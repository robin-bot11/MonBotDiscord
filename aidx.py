# help.py
import discord
from discord.ext import commands

EMBED_COLOR = 0x6b00cb

# 🔥 MAPPING COG → CATÉGORIE AFFICHÉE
COG_CATEGORIES = {
    "Moderation": "Modération",
    "Logs": "Logs",
    "Giveaway": "Giveaway",
    "Fun": "Fun",
    "Welcome": "Bienvenue",
    "Partenariat": "Partenariat",
    "Policy": "Règlement",
    "Verification": "Vérification",
    "Owner": "Owner",
    "Snipe": "Snipe"
}

# ------------------ VIEW MENU ------------------
class CategorySelect(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(
                label=label,
                description=f"Voir les commandes de {label}",
                value=name
            )
            for name, label in COG_CATEGORIES.items()
        ]
        super().__init__(placeholder="Sélectionnez une catégorie...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        cog_name = self.values[0]

        # Cherche le cog exact
        cog = None
        for c in self.bot.cogs.values():
            if c.qualified_name.lower() == cog_name.lower():
                cog = c
                break

        embed = discord.Embed(
            title=COG_CATEGORIES.get(cog_name, cog_name),
            color=EMBED_COLOR
        )

        if not cog:
            embed.description = "Aucune commande trouvée pour cette catégorie."
        else:
            cmds = cog.get_commands()
            if not cmds:
                embed.description = "Aucune commande trouvée pour cette catégorie."
            else:
                for cmd in cmds:
                    desc = cmd.help or "Pas de description disponible"
                    embed.add_field(name=f"+{cmd.name}", value=desc, inline=False)

        # Bouton pour revenir à l'accueil
        view = BackView(self.bot)
        await interaction.response.edit_message(embed=embed, view=view)


class CategoryView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)  # Pas de limite de temps
        self.bot = bot
        self.add_item(CategorySelect(bot))


class BackView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Retour", style=discord.ButtonStyle.primary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Menu d'aide",
            description=(
                "Tu as fait +help ?\n"
                "Bienvenue sur le menu d’aide du bot !\n"
                "Sélectionne une catégorie dans le menu ci-dessous pour voir les commandes disponibles.\n\n"
                "Certaines commandes sont protégées et réservées au propriétaire."
            ),
            color=EMBED_COLOR
        )
        await interaction.response.edit_message(embed=embed, view=CategoryView(self.bot))


# ------------------ COG ------------------
class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="Menu d'aide",
            description=(
                "Tu as fait +help ?\n"
                "Bienvenue sur le menu d’aide du bot !\n"
                "Sélectionne une catégorie dans le menu ci-dessous pour voir les commandes disponibles.\n\n"
                "Certaines commandes sont protégées et réservées au propriétaire."
            ),
            color=EMBED_COLOR
        )
        await ctx.send(embed=embed, view=CategoryView(self.bot))


# ------------------ SETUP ------------------
async def setup(bot):
    await bot.add_cog(Help(bot))
