import discord
from discord.ext import commands
from discord.ui import View, Select, Button

OWNER_ID = 1383790178522370058  # Remplace par ton ID
COLOR = 0x6b00cb

# ---------------- HELP VIEW ----------------
class HelpView(View):
    def __init__(self, author_id):
        super().__init__(timeout=None)
        self.author_id = author_id

        # Barre de sélection des catégories
        self.add_item(HelpSelect(author_id))

        # Bouton retour à l'accueil
        self.add_item(Button(label="Accueil", style=discord.ButtonStyle.secondary, custom_id="help_home"))

class HelpSelect(Select):
    def __init__(self, author_id):
        self.author_id = author_id

        # Options selon le propriétaire
        options = [
            discord.SelectOption(label="Fun", description="Commandes amusantes du bot"),
            discord.SelectOption(label="Modération", description="Commandes de modération"),
            discord.SelectOption(label="Bienvenue / Vérification", description="Setup du welcome et vérification"),
            discord.SelectOption(label="Logs", description="Commandes pour gérer les logs"),
            discord.SelectOption(label="Snipe", description="Commandes pour snipe messages supprimés")
        ]
        # Ajouter Owner seulement si c'est le propriétaire
        if self.author_id == OWNER_ID:
            options.append(discord.SelectOption(label="Owner", description="Commandes protégées réservées au propriétaire"))

        super().__init__(placeholder="Sélectionnez une catégorie", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("❌ Ce menu n'est pas pour vous.", ephemeral=True)

        embed = get_category_embed(self.values[0])
        await interaction.response.edit_message(embed=embed, view=self.view)

# ---------------- EMBEDS PAR CATÉGORIE ----------------
def get_category_embed(category):
    if category == "Fun":
        embed = discord.Embed(title="📂 Fun", color=COLOR)
        embed.add_field(name="+papa", value="Mon papa ? 𝐃𝐄𝐔𝐒\nLe légendaire pilier du serveur.", inline=False)

    elif category == "Modération":
        embed = discord.Embed(title="📂 Modération", color=COLOR)
        embed.add_field(name="+kick", value="Expulse un membre du serveur.", inline=False)
        embed.add_field(name="+ban", value="Bannit un membre du serveur.", inline=False)
        embed.add_field(name="+unban", value="Débannit un membre via son ID.", inline=False)
        embed.add_field(name="+mute", value="Mute un membre en lui donnant le rôle 'Muted'.", inline=False)
        embed.add_field(name="+unmute", value="Retire le rôle 'Muted' à un membre.", inline=False)
        embed.add_field(name="+timeout", value="Met un membre en timeout (minutes).", inline=False)
        embed.add_field(name="+giverole", value="Donne un rôle à un membre.", inline=False)
        embed.add_field(name="+takerole", value="Retire un rôle à un membre.", inline=False)
        embed.add_field(name="+warn", value="Avertit un membre.", inline=False)
        embed.add_field(name="+warns", value="Affiche les warns d'un membre.", inline=False)
        embed.add_field(name="+unwarn", value="Supprime un warn spécifique.", inline=False)
        embed.add_field(name="+purge", value="Supprime un nombre spécifique de messages.", inline=False)
        embed.add_field(name="+purgeall", value="Supprime tous les messages du salon.", inline=False)

    elif category == "Bienvenue / Vérification":
        embed = discord.Embed(title="📂 Bienvenue / Vérification", color=COLOR)
        embed.add_field(name="+setupverify", value="Configurer la vérification avec emoji", inline=False)
        embed.add_field(name="+setwelcome", value="Configurer le welcome simple (texte)", inline=False)
        embed.add_field(name="+setwelcomeembed", value="Configurer le welcome en embed", inline=False)
        embed.add_field(name="+togglewelcome", value="Activer / désactiver le welcome", inline=False)

    elif category == "Logs":
        embed = discord.Embed(title="📂 Logs", color=COLOR)
        embed.add_field(name="+logchannel", value="Configure le salon des logs", inline=False)
        embed.add_field(name="+loglevel", value="Affiche ou change le niveau de logs", inline=False)
        embed.add_field(name="+snipe", value="Récupère le dernier message supprimé.", inline=False)

    elif category == "Snipe":
        embed = discord.Embed(title="📂 Snipe", color=COLOR)
        embed.add_field(name="+snipe", value="Récupère le dernier message supprimé.", inline=False)

    elif category == "Owner":
        embed = discord.Embed(title="📂 Owner", color=COLOR)
        embed.add_field(name="+ping", value="Vérifie si le bot répond. — Protégée / Owner", inline=False)
        embed.add_field(name="+dm", value="Envoie un message privé à un utilisateur. — Protégée / Owner", inline=False)
        embed.add_field(name="+backupconfig", value="Sauvegarde la configuration. — Protégée / Owner", inline=False)
        embed.add_field(name="+restoreconfig", value="Restaure la configuration. — Protégée / Owner", inline=False)
        embed.add_field(name="+resetwarns", value="Supprime tous les warns. — Protégée / Owner", inline=False)
        embed.add_field(name="+checkrole", value="Affiche les permissions d’un rôle. — Protégée / Owner", inline=False)
        embed.add_field(name="+checkchannel", value="Affiche les informations d’un salon. — Protégée / Owner", inline=False)
        embed.add_field(name="+checkmember", value="Affiche les infos d’un membre. — Protégée / Owner", inline=False)
        embed.add_field(name="+listbots", value="Liste les bots sur le serveur. — Protégée / Owner", inline=False)
        embed.add_field(name="+servers", value="Liste les serveurs du bot. — Protégée / Owner", inline=False)
        embed.add_field(name="+invite", value="Crée une invitation pour un serveur. — Protégée / Owner", inline=False)
        embed.add_field(name="+shutdownbot", value="Éteint le bot. — Protégée / Owner", inline=False)
        embed.add_field(name="+restartbot", value="Redémarre le bot. — Protégée / Owner", inline=False)
        embed.add_field(name="+eval", value="Évalue du code Python. — Protégée / Owner", inline=False)
        embed.add_field(name="+status", value="Change le statut du bot. — Protégée / Owner", inline=False)
        embed.add_field(name="+setprefix", value="Change le préfixe du bot. — Protégée / Owner", inline=False)

    else:
        embed = discord.Embed(title="Aucune commande trouvée pour cette catégorie", color=COLOR)
    return embed

# ---------------- COMMANDE +HELP ----------------
class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="📖 Menu d'aide",
            description=(
                "Tu as fait +help ?\n\n"
                "Bienvenue sur le menu d’aide du bot, sélectionne une catégorie dans le menu déroulant pour voir les commandes.\n\n"
                "Certaines commandes sont protégées et réservées au propriétaire."
            ),
            color=COLOR
        )
        view = HelpView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

# ---------------- SETUP ----------------
async def setup(bot):
    await bot.add_cog(Help(bot))
