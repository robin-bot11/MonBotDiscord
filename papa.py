import discord
from discord.ext import commands

OWNER_ID = 1383790178522370058
COLOR = 0x6b00cb

# ---------------- HELP OWNER PAPA ----------------
class HelpPapaDropdown(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Commandes de base"),
            discord.SelectOption(label="Config / Backup"),
            discord.SelectOption(label="Check"),
            discord.SelectOption(label="Listes"),
            discord.SelectOption(label="Invite"),
            discord.SelectOption(label="Système"),
            discord.SelectOption(label="Eval"),
            discord.SelectOption(label="Statut / Reload"),
            discord.SelectOption(label="Info / Mémoire / Latence"),
            discord.SelectOption(label="Lock / Unlock Bot")
        ]
        super().__init__(placeholder="Sélectionnez une catégorie", min_values=1, max_values=1, options=options)

        # Commandes classées avec description détaillée
        self.commands_dict = {
            "Commandes de base": [
                "+ping — Vérifie si le bot est en ligne",
                "+dm <user_id> <message> — Envoie un message privé à un utilisateur"
            ],
            "Config / Backup": [
                "+backupconfig — Sauvegarde la configuration du bot",
                "+restoreconfig — Restaure la configuration sauvegardée",
                "+resetwarns <member_id> — Supprime tous les warns d'un membre sur le serveur"
            ],
            "Check": [
                "+checkrole <role_id> — Affiche toutes les permissions d'un rôle",
                "+checkchannel <channel_id> — Affiche les informations d'un salon",
                "+checkmember <member_id> — Affiche les rôles d'un membre"
            ],
            "Listes": [
                "+listbots — Liste tous les bots du serveur",
                "+servers [page] — Liste les serveurs du bot (DM)"
            ],
            "Invite": [
                "+invite <guild_id> — Crée une invitation pour le serveur spécifié"
            ],
            "Système": [
                "+shutdownbot — Éteint le bot de façon sécurisée",
                "+restartbot — Redémarre le bot"
            ],
            "Eval": [
                "+eval <code> — Exécute du code Python (Owner uniquement)"
            ],
            "Statut / Reload": [
                "+status <type> <texte> — Change le statut du bot (online/dnd/idle/invisible)",
                "+reload <cog> — Recharge un cog spécifique",
                "+reloadall — Recharge tous les cogs du bot"
            ],
            "Info / Mémoire / Latence": [
                "+botinfo — Affiche les informations du bot, serveurs, latence et mémoire",
                "+latency — Affiche la latence du bot en ms",
                "+memory — Affiche la mémoire utilisée par le bot"
            ],
            "Lock / Unlock Bot": [
                "+lockbot — Verrouille le bot, interdit l'utilisation des commandes sauf Owner",
                "+unlockbot — Déverrouille le bot",
                "+leaveserver <guild_id> — Fait quitter le bot d'un serveur spécifique"
            ]
        }

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        commands_list = self.commands_dict.get(category, ["⚠️ Pas de commandes trouvées"])
        embed = discord.Embed(
            title=f"💜 Owner Commands — {category}",
            description="\n".join(commands_list),
            color=COLOR
        )
        view = HomeOwnerView(self.bot)
        view.add_item(self)
        await interaction.response.edit_message(embed=embed, view=view)

# ---------------- HELP OWNER VIEW ----------------
class HelpOwnerView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(HelpPapaDropdown(bot))

# ---------------- BOUTON ACCUEIL ----------------
class HomeOwnerView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Accueil", style=discord.ButtonStyle.primary)
    async def home_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != OWNER_ID:
            return await interaction.response.send_message("⛔ Vous n'êtes pas autorisé.", ephemeral=True)
        embed = discord.Embed(
            title="💜 Menu d'aide Owner",
            description="Voici toutes les commandes Owner/Créateur disponibles. Utilise le menu pour naviguer.",
            color=COLOR
        )
        await interaction.response.edit_message(embed=embed, view=HelpOwnerView(self.bot))

# ---------------- HELP PAPA COMMAND ----------------
class HelpPapaCommand(commands.Cog):
    """Menu d'aide Owner/Créateur avec descriptions détaillées"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help.papa")
    async def help_papa(self, ctx):
        if ctx.author.id != OWNER_ID:
            return await ctx.send("⛔ Cette commande est réservée au propriétaire @𝐃𝐄𝐔𝐒")
        embed = discord.Embed(
            title="💜 Menu d'aide Owner",
            description="Voici toutes les commandes Owner/Créateur disponibles. Utilise le menu ci-dessous pour naviguer.",
            color=COLOR
        )
        await ctx.send(embed=embed, view=HelpOwnerView(self.bot))

# ---------------- SETUP ----------------
async def setup(bot):
    await bot.add_cog(HelpPapaCommand(bot))
