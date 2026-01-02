# help.py
import discord
from discord.ext import commands
from discord.ui import View, Select, Button

COLOR = 0x6b00cb

# -------------------- COMMANDES PAR CATÉGORIE --------------------
COMMANDS = {
    "Bienvenue / Vérification": [
        {"name": "+setupverify", "desc": "Configurer la vérification avec emoji"},
        {"name": "+setwelcome", "desc": "Configurer le welcome simple (texte)"},
        {"name": "+setwelcomeembed", "desc": "Configurer le welcome en embed"},
        {"name": "+togglewelcome", "desc": "Activer / désactiver le welcome sans supprimer la config"}
    ],
    "Fun": [
        {"name": "+papa", "desc": "Affiche un message fun pour le papa du serveur"}
    ],
    "Modération": [
        {"name": "+kick", "desc": "Expulse un membre du serveur"},
        {"name": "+ban", "desc": "Bannit un membre du serveur"},
        {"name": "+unban", "desc": "Débannit un utilisateur via son ID"},
        {"name": "+mute", "desc": "Mute un membre avec le rôle 'Muted'"},
        {"name": "+unmute", "desc": "Retire le rôle 'Muted' à un membre"},
        {"name": "+timeout", "desc": "Met un membre en timeout (minutes)"},
        {"name": "+giverole", "desc": "Donne un rôle à un membre"},
        {"name": "+takerole", "desc": "Retire un rôle à un membre"},
        {"name": "+warn", "desc": "Avertit un membre"},
        {"name": "+warns", "desc": "Affiche les warns d'un membre"},
        {"name": "+unwarn", "desc": "Supprime un warn spécifique"},
        {"name": "+purge", "desc": "Supprime un nombre spécifique de messages"},
        {"name": "+purgeall", "desc": "Supprime tous les messages du salon"}
    ],
    "Logs / Snipe": [
        {"name": "+snipe", "desc": "Affiche le dernier message supprimé"},
        {"name": "+editsnipe", "desc": "Affiche le dernier message édité"},
        {"name": "+logrole", "desc": "Logs de rôle"},
        {"name": "+logmod", "desc": "Logs modération"},
        {"name": "+logvoice", "desc": "Logs vocaux"},
        {"name": "+logchannel", "desc": "Logs de création/suppression/modification de salon"},
        {"name": "+logmessage", "desc": "Logs messages supprimés/édités"}
    ]
}

# -------------------- MENU DÉROULANT --------------------
class HelpSelect(Select):
    def __init__(self, user_id):
        options = [discord.SelectOption(label=cat) for cat in COMMANDS.keys()]
        super().__init__(placeholder="Sélectionnez une catégorie", min_values=1, max_values=1, options=options)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Ce menu n'est pas pour vous.", ephemeral=True)

        category = self.values[0]
        cmds = COMMANDS.get(category, [])
        if not cmds:
            description = "Aucune commande trouvée pour cette catégorie."
        else:
            description = ""
            for cmd in cmds:
                desc = cmd["desc"] if cmd.get("desc") else "Pas de description"
                description += f"**{cmd['name']}** — {desc}\n"

        embed = discord.Embed(title=f"📂 {category}", description=description, color=COLOR)
        await interaction.response.edit_message(embed=embed, view=HelpView(self.user_id))

# -------------------- VUE --------------------
class HelpView(View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.add_item(HelpSelect(user_id))

    @discord.ui.button(label="Retour", style=discord.ButtonStyle.secondary, custom_id="help_back_button")
    async def back_button(self, button: Button, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Ce bouton n'est pas pour vous.", ephemeral=True)

        embed = discord.Embed(
            title="📖 Menu d'aide",
            description=(
                "Tu as fait +help ?\n\n"
                "Bienvenue sur le menu d’aide du bot !\n"
                "Sélectionne une catégorie dans le menu ci-dessous pour voir les commandes disponibles.\n\n"
                "Certaines commandes sont protégées et réservées au propriétaire."
            ),
            color=COLOR
        )

        await interaction.response.edit_message(embed=embed, view=HelpView(self.user_id))

# -------------------- COG --------------------
class Help(commands.Cog):
    """Menu d'aide avec sélection de catégorie"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="📖 Menu d'aide",
            description=(
                "Tu as fait +help ?\n\n"
                "Bienvenue sur le menu d’aide du bot !\n"
                "Sélectionne une catégorie dans le menu ci-dessous pour voir les commandes disponibles.\n\n"
                "Certaines commandes sont protégées et réservées au propriétaire."
            ),
            color=COLOR
        )
        await ctx.send(embed=embed, view=HelpView(ctx.author.id))

# -------------------- SETUP --------------------
async def setup(bot):
    await bot.add_cog(Help(bot))
