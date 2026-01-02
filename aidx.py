import discord
from discord.ext import commands

EMBED_COLOR = 0x6b00cb

# 🔥 MAPPING RÉEL : COG NAME EXACT → CATÉGORIE
COG_CATEGORIES = {
    "Moderation": "📂 Modération",
    "Partenariat": "📂 Partenariat",
    "Policy": "📂 Règlement",
    "Snipe": "📂 Vérification"
}

class CategoryView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot

        for cog_name, label in COG_CATEGORIES.items():
            # N’ajoute le bouton QUE si le cog est chargé
            if bot.get_cog(cog_name):
                self.add_item(CategoryButton(cog_name, label, bot))


class CategoryButton(discord.ui.Button):
    def __init__(self, cog_name, label, bot):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary,
            custom_id=f"help_{cog_name}"
        )
        self.cog_name = cog_name
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        cog = self.bot.get_cog(self.cog_name)

        embed = discord.Embed(
            title=COG_CATEGORIES.get(self.cog_name, self.cog_name),
            color=EMBED_COLOR
        )

        if not cog:
            embed.description = "Aucune commande trouvée pour cette catégorie."
        else:
            commands_list = cog.get_commands()
            if not commands_list:
                embed.description = "Aucune commande trouvée pour cette catégorie."
            else:
                for cmd in commands_list:
                    embed.add_field(
                        name=f"+{cmd.name}",
                        value=cmd.help or "Pas de description",
                        inline=False
                    )

        await interaction.response.edit_message(
            embed=embed,
            view=BackView(self.bot)
        )


class BackView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot

    @discord.ui.button(label="⬅️ Retour", style=discord.ButtonStyle.primary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📖 Menu d'aide",
            description="Sélectionne une catégorie ci-dessous",
            color=EMBED_COLOR
        )
        await interaction.response.edit_message(
            embed=embed,
            view=CategoryView(self.bot)
        )


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="📖 Menu d'aide",
            description="Sélectionne une catégorie ci-dessous",
            color=EMBED_COLOR
        )
        await ctx.send(embed=embed, view=CategoryView(self.bot))


async def setup(bot):
    await bot.add_cog(Help(bot))
