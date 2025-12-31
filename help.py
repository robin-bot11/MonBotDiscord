import discord
from discord.ext import commands

OWNER_ID = 1383790178522370058
COLOR = 0x6b00cb

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        is_owner = ctx.author.id == OWNER_ID

        embed = discord.Embed(
            title="Aide du bot",
            description="Voici les commandes disponibles",
            color=COLOR
        )

        # --- Modération ---
        embed.add_field(
            name="Modération",
            value=(
                "+kick <ID> <raison>\n"
                "+ban <ID> <raison>\n"
                "+uban <ID>\n"
                "+mute <ID>\n"
                "+umute <ID>\n"
                "+warn <ID> <raison>\n"
                "+warns <ID>\n"
                "+delwarn <ID>"
            ),
            inline=False
        )

        # --- Giveaway ---
        embed.add_field(
            name="Giveaway",
            value=(
                "+gyveaway <durée> <récompense>\n"
                "+gyend <ID>\n"
                "+gyrestart <ID>\n"
                "+gyrole <ID rôle>"
            ),
            inline=False
        )

        # --- Autres commandes ---
        embed.add_field(
            name="Autres",
            value="+papa\n+snipe",
            inline=False
        )

        # --- Commandes propriétaire ---
        if is_owner:
            embed.add_field(
                name="Propriétaire",
                value=(
                    "+shutdown\n"
                    "+restart\n"
                    "+poweron\n"
                    "+status <texte>\n"
                    "+eval <code>\n"
                    "+backupconfig\n"
                    "+restoreconfig"
                ),
                inline=False
            )

        # --- Envoi du MP ---
        try:
            await ctx.author.send(embed=embed)
            await ctx.reply("La liste des commandes a été envoyée en message privé.")
        except discord.Forbidden:
            await ctx.reply("Je ne peux pas t’envoyer de message privé.")

def setup(bot):
    bot.add_cog(Help(bot))
