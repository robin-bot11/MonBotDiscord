# help.py
from discord.ext import commands
import discord
from discord.ui import View, Select, Button

COLOR = 0x6b00cb
OWNER_ID = 1383790178522370058  # Ton ID

# -------------------- Vue du Menu --------------------
class HelpSelect(Select):
    def __init__(self, bot, member):
        self.bot = bot
        self.member = member
        options = []

        # On fixe l'ordre exact des catégories souhaitées
        categories_order = ["Fun", "Moderation", "Bienvenue / Vérification", "Logs", "Snipe", "Owner"]
        for name in categories_order:
            cog = bot.cogs.get(name)
            if not cog:
                continue
            # Cacher Owner si l'utilisateur n'est pas propriétaire
            if name.lower() == "owner" and member.id != OWNER_ID:
                continue
            options.append(discord.SelectOption(label=name, description=cog.__doc__ or "Pas de description"))

        super().__init__(placeholder="Sélectionnez une catégorie", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        cog_name = self.values[0]
        embed = discord.Embed(title=f"📂 {cog_name}", color=COLOR)

        # Commandes par catégorie
        if cog_name == "Bienvenue / Vérification":
            cmds = [
                ("setupverify", "Configurer la vérification avec emoji"),
                ("setwelcome", "Configurer le welcome simple (texte)"),
                ("setwelcomeembed", "Configurer le welcome en embed"),
                ("togglewelcome", "Activer / désactiver le welcome sans supprimer la config")
            ]
        elif cog_name == "Owner":
            cmds = [
                ("ping", "Pas de description — Protégée / Owner"),
                ("dm", "Pas de description — Protégée / Owner"),
                ("backupconfig", "Pas de description — Protégée / Owner"),
                ("restoreconfig", "Pas de description — Protégée / Owner"),
                ("resetwarns", "Pas de description — Protégée / Owner"),
                ("checkrole", "Pas de description — Protégée / Owner"),
                ("checkchannel", "Pas de description — Protégée / Owner"),
                ("checkmember", "Pas de description — Protégée / Owner"),
                ("listbots", "Pas de description — Protégée / Owner"),
                ("servers", "Pas de description — Protégée / Owner"),
                ("invite", "Pas de description — Protégée / Owner"),
                ("shutdownbot", "Pas de description — Protégée / Owner"),
                ("restartbot", "Pas de description — Protégée / Owner"),
                ("eval", "Pas de description — Protégée / Owner")
            ]
        else:
            cog = self.bot.cogs.get(cog_name)
            if not cog:
                cmds = []
            else:
                cmds = []
                for cmd in cog.get_commands():
                    desc = cmd.help or "Pas de description"
                    if cog_name == "Owner" or getattr(cmd, "hidden", False):
                        if self.member.id == OWNER_ID:
                            desc += " — Protégée / Owner"
                        else:
                            continue
                    cmds.append((cmd.name, desc))

        if not cmds:
            embed.description = "Aucune commande trouvée pour cette catégorie."
        else:
            for name, desc in cmds:
                embed.add_field(name=f"+{name}", value=desc, inline=False)

        view = View(timeout=None)
        view.add_item(HelpSelect(self.bot, self.member))
        view.add_item(Button(label="🏠 Retour", style=discord.ButtonStyle.gray, custom_id="help_home"))
        await interaction.response.edit_message(embed=embed, view=view)

# -------------------- Vue Accueil --------------------
class HelpView(View):
    def __init__(self, bot, member):
        super().__init__(timeout=None)
        self.bot = bot
        self.member = member
        self.add_item(HelpSelect(bot, member))
        self.add_item(Button(label="🏠 Retour", style=discord.ButtonStyle.gray, custom_id="help_home"))

    @discord.ui.button(label="🏠 Retour", style=discord.ButtonStyle.gray, custom_id="help_home")
    async def back_button(self, button: Button, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📖 Menu d'aide",
            description=(
                "Tu as fait +help ?\n"
                "Bienvenue sur le menu d’aide du bot !\n"
                "Sélectionne une catégorie dans le menu ci-dessous pour voir les commandes disponibles.\n\n"
                "Certaines commandes sont protégées et réservées au propriétaire."
            ),
            color=COLOR
        )
        await interaction.response.edit_message(embed=embed, view=HelpView(self.bot, self.member))

# -------------------- Commande Help --------------------
class HelpCog(commands.Cog):
    """Menu d'aide du bot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="📖 Menu d'aide",
            description=(
                "Tu as fait +help ?\n"
                "Bienvenue sur le menu d’aide du bot !\n"
                "Sélectionne une catégorie dans le menu ci-dessous pour voir les commandes disponibles.\n\n"
                "Certaines commandes sont protégées et réservées au propriétaire."
            ),
            color=COLOR
        )
        await ctx.send(embed=embed, view=HelpView(self.bot, ctx.author))

# -------------------- Setup --------------------
async def setup(bot):
    await bot.add_cog(HelpCog(bot))
