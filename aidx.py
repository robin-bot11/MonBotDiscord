import discord
from discord.ext import commands

EMBED_COLOR = 0x6b00cb

# 🔥 MAPPING COG → CATÉGORIE AFFICHÉE
COG_CATEGORIES = {
    "Moderation": "📂 Modération",
    "Logs": "📂 Logs",
    "Giveaway": "📂 Giveaway",
    "Fun": "📂 Fun",
    "Welcome": "📂 Bienvenue",
    "Partenariat": "📂 Partenariat",
    "Reglement": "📂 Règlement",
    "Verification": "📂 Vérification",
    "Owner": "📂 Owner"
}

class CategoryView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot

        for cog_name, label in COG_CATEGORIES.items():
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
            cmds = cog.get_commands()
            if not cmds:
                embed.description = "Aucune commande trouvée pour cette catégorie."
            else:
                for cmd in cmds:
                    desc = cmd.help or "Pas de description"
                    embed.add_field(
                        name=f"+{cmd.name}",
                        value=desc,
                        inline=False
                    )

        view = BackView(self.bot)
        await interaction.response.edit_message(embed=embed, view=view)


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
        await interaction.response.edit_message(embed=embed, view=CategoryView(self.bot))


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
