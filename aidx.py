# help.py
from discord.ext import commands
import discord
from discord.ui import View, Button, Select

COLOR = 0x6b00cb
OWNER_ID = 1383790178522370058

# -------------------- Menu Select --------------------
class HelpSelect(Select):
    def __init__(self, user_id, bot):
        self.user_id = user_id
        self.bot = bot

        options = [
            discord.SelectOption(label="Bienvenue / Vérification", description="Commandes de bienvenue et vérification"),
            discord.SelectOption(label="Fun", description="Commandes amusantes"),
            discord.SelectOption(label="Modération", description="Commandes pour gérer le serveur"),
            discord.SelectOption(label="Logs", description="Commandes liées aux logs"),
            discord.SelectOption(label="Snipe", description="Commandes pour snipe messages supprimés"),
        ]

        super().__init__(placeholder="Sélectionnez une catégorie", min_values=1, max_values=1, options=options, custom_id=f"help_select_{user_id}")

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Ce menu n'est pas pour vous.", ephemeral=True)

        embed = discord.Embed(title="📂 Menu d'aide", color=COLOR)

        if self.values[0] == "Bienvenue / Vérification":
            embed.description = (
                "+setupverify — Configurer la vérification avec emoji\n"
                "+setwelcome — Configurer le welcome simple (texte)\n"
                "+setwelcomeembed — Configurer le welcome en embed\n"
                "+togglewelcome — Activer / désactiver le welcome sans supprimer la config"
            )
        elif self.values[0] == "Fun":
            embed.description = (
                "+papa — Envoie un message hommage au propriétaire du serveur"
            )
        elif self.values[0] == "Modération":
            embed.description = (
                "+kick <ID> [raison] — Expulse un membre\n"
                "+ban <ID> [raison] — Bannit un membre\n"
                "+unban <ID> — Débannit un membre\n"
                "+mute <ID> [raison] — Mute un membre\n"
                "+unmute <ID> — Unmute un membre\n"
                "+timeout <ID> <minutes> — Timeout d'un membre\n"
                "+giverole <ID> <roleID> — Donne un rôle\n"
                "+takerole <ID> <roleID> — Retire un rôle\n"
                "+warn <ID> [raison] — Avertit un membre\n"
                "+warns <ID> — Liste des warns\n"
                "+unwarn <ID> <num> — Supprime un warn\n"
                "+purge <nombre> — Supprime des messages\n"
                "+purgeall — Supprime tous les messages du salon"
            )
        elif self.values[0] == "Logs":
            embed.description = (
                "+logchannel — Configurer le salon logs\n"
                "+logrole — Configurer les logs rôles\n"
                "+logmod — Configurer les logs modérations\n"
                "+logvoice — Configurer les logs vocaux\n"
                "+logmessage — Configurer les logs messages"
            )
        elif self.values[0] == "Snipe":
            embed.description = (
                "+snipe — Affiche le dernier message supprimé\n"
                "+esnipe — Affiche le dernier message édité"
            )

        # Bouton retour
        view = View(timeout=None)
        view.add_item(Button(label="Retour", style=discord.ButtonStyle.secondary, custom_id=f"help_back_{self.user_id}"))
        await interaction.response.edit_message(embed=embed, view=view)


# -------------------- Cog Help --------------------
class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        owner_hidden = ctx.author.id != OWNER_ID

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

        view = View(timeout=None)
        view.add_item(HelpSelect(ctx.author.id, self.bot))

        await ctx.send(embed=embed, view=view)

# -------------------- Setup --------------------
async def setup(bot):
    await bot.add_cog(Help(bot))
