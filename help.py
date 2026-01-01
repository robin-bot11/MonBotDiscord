from discord.ext import commands
import discord

COLOR = 0x6b00cb
OWNER_ID = 1383790178522370058

class HelpSelect(discord.ui.Select):
    def __init__(self, is_owner: bool):
        options = [
            discord.SelectOption(label="Modération", emoji="🛡️"),
            discord.SelectOption(label="Giveaway", emoji="🎉"),
            discord.SelectOption(label="Fun", emoji="😂"),
            discord.SelectOption(label="Bienvenue", emoji="👋"),
            discord.SelectOption(label="Partenariat", emoji="🤝"),
            discord.SelectOption(label="Règlement", emoji="📜"),
        ]
        if is_owner:
            options.append(discord.SelectOption(label="Owner", emoji="👑"))

        super().__init__(
            placeholder="📖 Choisis une catégorie",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        embed = discord.Embed(color=COLOR)

        # ---------------- Modération ----------------
        if category == "Modération":
            embed.title = "🛡️ Modération"
            embed.description = (
                "**+kick `<ID> <raison>`**\n↳ Permission : Kick Members\n\n"
                "**+ban `<ID> <raison>`**\n↳ Permission : Ban Members\n\n"
                "**+uban `<ID>`**\n↳ Permission : Ban Members\n\n"
                "**+mute `<ID> <raison>`**\n↳ Permission : Manage Roles\n\n"
                "**+unmute `<ID>`**\n↳ Permission : Manage Roles\n\n"
                "**+warn `<ID> <raison>`**\n↳ Permission : Manage Messages\n\n"
                "**+unwarn `<ID> <num>`**\n↳ Permission : Manage Messages\n\n"
                "**+warns `<ID>`**\n↳ Permission : Manage Messages\n\n"
                "**+purge `<nombre>`**\n↳ Permission : Manage Messages\n\n"
                "**+purgeall**\n↳ Permission : Administrateur"
            )

        # ---------------- Giveaway ----------------
        elif category == "Giveaway":
            embed.title = "🎉 Giveaway"
            embed.description = (
                "**+gyveaway `<durée> <récompense>`**\n↳ Permission : Rôle autorisé\n\n"
                "**+gyrole `<@rôle>`**\n↳ Permission : Administrateur\n\n"
                "**+gyend `<ID>`**\n↳ Permission : Rôle autorisé\n\n"
                "**+gyrestart `<ID>`**\n↳ Permission : Rôle autorisé"
            )

        # ---------------- Fun ----------------
        elif category == "Fun":
            embed.title = "😂 Fun"
            embed.description = "**+papa**\n↳ Permission : Aucune"

        # ---------------- Bienvenue ----------------
        elif category == "Bienvenue":
            embed.title = "👋 Bienvenue"
            embed.description = (
                "**+setwelcome `<message>`**\n↳ Permission : Administrateur\n\n"
                "**+setwelcomechannel `<#channel>`**\n↳ Permission : Administrateur"
            )

        # ---------------- Partenariat ----------------
        elif category == "Partenariat":
            embed.title = "🤝 Partenariat"
            embed.description = (
                "**+setpartnerrole `<@rôle>`**\n↳ Permission : Owner\n\n"
                "**+setpartnersalon `<#channel>`**\n↳ Permission : Owner"
            )

        # ---------------- Règlement ----------------
        elif category == "Règlement":
            embed.title = "📜 Règlement"
            embed.description = (
                "**+reglement `<titre> <texte> [role] [image] [emoji] [texte_bouton]`**\n"
                "↳ Permission : Administrateur"
            )

        # ---------------- Owner ----------------
        elif category == "Owner":
            if interaction.user.id != OWNER_ID:
                return await interaction.response.send_message(
                    "⛔ Accès refusé.",
                    ephemeral=True
                )
            embed.title = "👑 Owner"
            embed.description = (
                "**+ping**\n↳ Permission : Owner\n\n"
                "**+dm `<ID> <message>`**\n↳ Permission : Owner\n\n"
                "**+backupconfig**\n↳ Permission : Owner\n\n"
                "**+restoreconfig**\n↳ Permission : Owner"
            )

        await interaction.response.edit_message(embed=embed, view=self.view)


class HelpView(discord.ui.View):
    def __init__(self, is_owner: bool):
        super().__init__(timeout=180)
        self.add_item(HelpSelect(is_owner))


class Aide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        is_owner = ctx.author.id == OWNER_ID
        embed = discord.Embed(
            title="📖 Aide du bot",
            description="Utilise le menu déroulant pour afficher les commandes par catégorie.",
            color=COLOR
        )
        try:
            await ctx.author.send(embed=embed, view=HelpView(is_owner))
            await ctx.reply("📬 **Help envoyé en message privé.**", mention_author=False)
        except discord.Forbidden:
            await ctx.reply("❌ Impossible de t’envoyer un MP.")

async def setup(bot):
    await bot.add_cog(Aide(bot))
