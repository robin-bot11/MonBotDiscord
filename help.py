from discord.ext import commands
import discord

COLOR = 0x6b00cb
OWNER_ID = 1383790178522370058

class HelpSelect(discord.ui.Select):
    def __init__(self, is_owner):
        options = [
            discord.SelectOption(label="Modération", emoji="🛡️"),
            discord.SelectOption(label="Logs", emoji="📑"),
            discord.SelectOption(label="Giveaway", emoji="🎉"),
            discord.SelectOption(label="Fun", emoji="😂"),
            discord.SelectOption(label="Bienvenue", emoji="👋"),
            discord.SelectOption(label="Partenariat", emoji="🤝"),
            discord.SelectOption(label="Règlement", emoji="📜"),
        ]
        if is_owner:
            options.append(discord.SelectOption(label="Owner", emoji="👑"))

        super().__init__(placeholder="📂 Sélectionne une catégorie", options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(color=COLOR)
        cat = self.values[0]

        if cat == "Logs":
            embed.title = "📑 Logs"
            embed.description = (
                "**+setlog message `<#salon>`**\nLogs messages\n\n"
                "**+setlog mod `<#salon>`**\nLogs modération\n\n"
                "**+setlog channel `<#salon>`**\nLogs salons\n\n"
                "**+setlog voice `<#salon>`**\nLogs vocaux\n\n"
                "**+setlog member `<#salon>`**\nLogs membres\n\n"
                "**+setlog role `<#salon>`**\nLogs rôles"
            )

        await interaction.response.edit_message(embed=embed, view=self.view)

class HelpView(discord.ui.View):
    def __init__(self, is_owner):
        super().__init__(timeout=180)
        self.add_item(HelpSelect(is_owner))

class Aide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="📖 Centre d’aide",
            description=(
                "Bienvenue dans le **système d’aide interactif**.\n\n"
                "🔹 Toutes les commandes sont classées par catégorie\n"
                "🔹 Utilise le menu ci-dessous pour naviguer\n"
                "🔹 Les commandes Owner sont protégées\n\n"
                "**Préfixe : `+`**"
            ),
            color=COLOR
        )

        await ctx.author.send(embed=embed, view=HelpView(ctx.author.id == OWNER_ID))
        await ctx.reply("📬 **Aide envoyée en message privé.**", mention_author=False)

async def setup(bot):
    await bot.add_cog(Aide(bot))
