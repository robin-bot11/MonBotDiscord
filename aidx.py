# help.py
from discord.ext import commands
import discord

COLOR = 0x6b00cb

# ⚡ Priorité et emoji pour chaque cog
COG_INFO = {
    "Moderation": {"emoji": "🔨", "priority": 1},
    "Logx": {"emoji": "📜", "priority": 2},
    "MessageChannel": {"emoji": "✉️", "priority": 3},
    "Partenariat": {"emoji": "🤝", "priority": 4},
    "Policy": {"emoji": "📄", "priority": 5},
    "Snipe": {"emoji": "🔍", "priority": 6},
    "Help": {"emoji": "💜", "priority": 99},  # Toujours en dernier
}

# Exemple texte pour la page d'accueil
HOME_TEXT = (
    "💜 **Bienvenue dans le menu d'aide de MonBotDiscord !**\n\n"
    "Voici un aperçu de ce que chaque catégorie propose.\n"
    "Tu peux utiliser les commandes suivantes comme exemple :\n\n"
    "**Moderation** : +warn {user} {raison} | +kick {user}\n"
    "**Welcome** : +setwelcome {channel} {message} | {user}, {server}, {members}\n"
    "**Verification** : +setverification {role} {message} | +resettries {user}\n"
    "**Snipe** : +snipe (affiche le dernier message supprimé dans le salon)\n"
    "**Partenariat** : +setpartnerrole {role} | +setpartnerchannel {channel}\n\n"
    "Pour voir toutes les commandes d'une catégorie : +help <cog>\n"
    "Exemple : `+help Moderation`"
)

class Help(commands.Cog):
    """Commande +help interactive et complète, sans commandes Owner"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx, cog_name: str = None):
        """Affiche toutes les commandes ou celles d'un cog spécifique"""
        embed = discord.Embed(title="💜 Aide de MonBotDiscord", description=HOME_TEXT, color=COLOR)

        if cog_name:  # Affichage d'un cog spécifique
            cog = self.bot.get_cog(cog_name.capitalize())
            if not cog:
                return await ctx.send(f"❌ Cog `{cog_name}` introuvable.")
            
            commands_list = cog.get_commands()
            if not commands_list:
                return await ctx.send(f"❌ Aucune commande trouvée dans `{cog_name}`.")

            description = ""
            for cmd in commands_list:
                # Exemple de format pour chaque commande
                description += f"**+{cmd.name}** : {cmd.help or 'Pas de description'}\n"
            embed.title = f"💜 Commandes pour `{cog_name}`"
            embed.description = description
            await ctx.send(embed=embed)

        else:  # Affichage de toutes les cogs accessibles
            cogs_sorted = sorted(
                self.bot.cogs.items(),
                key=lambda x: COG_INFO.get(x[0], {"priority": 999})["priority"]
            )

            for cog_name, cog in cogs_sorted:
                # On saute les cogs Owner / Creator
                if cog_name.lower() in ["creator", "owner"]:
                    continue

                commands_list = cog.get_commands()
                if not commands_list:
                    continue

                description = ""
                for cmd in commands_list:
                    description += f"**+{cmd.name}** : {cmd.help or 'Pas de description'}\n"

                emoji = COG_INFO.get(cog_name, {}).get("emoji", "")
                embed.add_field(name=f"{emoji} {cog_name}", value=description, inline=False)

            embed.set_footer(text="Utilise +help <cog> pour voir les commandes d'une catégorie spécifique.")
            await ctx.send(embed=embed)


# -------------------- Setup --------------------
async def setup(bot):
    await bot.add_cog(Help(bot))
