# papa.py
import discord
from discord.ext import commands
import asyncio
import traceback
import psutil
import os
import time

OWNER_ID = 1383790178522370058
COLOR = 0x6b00cb
SNIPE_EXPIRATION = 86400  # 24h pour expiration snipes

class Owner(commands.Cog):
    """Toutes les commandes Owner/Créateur, incluant le contrôle des snipes"""

    def __init__(self, bot):
        self.bot = bot
        self.locked = False

    # ---------------- UTIL ----------------
    def is_owner(self, ctx):
        return ctx.author.id == OWNER_ID

    async def check_owner(self, ctx):
        if not self.is_owner(ctx):
            await ctx.send("⛔ Vous n'êtes pas autorisé à utiliser cette commande.")
            return False
        return True

    async def safe_send(self, ctx, content=None, embed=None, dm=False):
        try:
            if dm:
                if embed:
                    await ctx.author.send(embed=embed)
                else:
                    await ctx.author.send(content)
            else:
                if embed:
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(content)
        except discord.Forbidden:
            pass

    async def cog_check(self, ctx):
        if self.locked and not self.is_owner(ctx):
            await ctx.send("⛔ Le bot est actuellement verrouillé.")
            return False
        return True

    # ---------------- COMMANDES DE BASE ----------------
    @commands.command(name="owner_ping")
    async def owner_ping(self, ctx):
        if not await self.check_owner(ctx): return
        await self.safe_send(ctx, "✅ Le bot est en ligne.")

    # ... toutes les autres commandes Owner ici (inchangées) ...

    # ---------------- HELP PAPA ----------------
class HelpOwnerDropdown(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Owner Commands", description="Toutes les commandes Owner/Créateur")
        ]
        super().__init__(placeholder="Sélectionnez une catégorie", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="💜 Menu d'aide",
            description="[ + ] 𝐑𝐨𝐛𝐢𝐧\n\n**Tu as fait +help ?**\n\nVoici toutes les commandes Owner/Créateur disponibles.",
            color=COLOR
        )
        owner_commands = [c for c in interaction.client.get_cog("Owner").get_commands() if not c.hidden]
        commands_text = ""
        for cmd in owner_commands:
            commands_text += f"**+{cmd.name}** : {cmd.help or 'Pas de description'}\n"
        embed.add_field(name="Owner Commands", value=commands_text or "Aucune commande trouvée", inline=False)
        view = HomeOwnerButtonView(self.bot)
        view.add_item(self)
        await interaction.response.edit_message(embed=embed, view=view)

class HelpOwnerView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(HelpOwnerDropdown(bot))

class HomeOwnerButtonView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Accueil", style=discord.ButtonStyle.primary)
    async def home_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="💜 Menu d'aide",
            description="[ + ] 𝐑𝐨𝐛𝐢𝐧\n\n**Tu as fait +help ?**\n\nUtilise le menu de sélection ci-dessous pour choisir une catégorie.\nLes permissions requises sont indiquées pour chaque commande.",
            color=COLOR
        )
        await interaction.response.edit_message(embed=embed, view=HelpOwnerView(self.bot))

# Commande pour afficher le menu Owner amélioré
    @commands.command(name="help.papa")
    async def help_papa(self, ctx):
        if not self.is_owner(ctx):
            return await self.safe_send(ctx, "⛔ Cette commande est réservée au propriétaire @𝐃𝐄𝐔𝐒")
        embed = discord.Embed(
            title="💜 Menu d'aide",
            description="[ + ] 𝐑𝐨𝐛𝐢𝐧\n\n**Tu as fait +help ?**\n\nUtilise le menu de sélection ci-dessous pour choisir une catégorie.\nLes permissions requises sont indiquées pour chaque commande.",
            color=COLOR
        )
        await self.safe_send(ctx, embed=embed)
        await ctx.send(view=HelpOwnerView(self.bot))


# ---------------- SETUP ----------------
async def setup(bot):
    await bot.add_cog(Owner(bot))
