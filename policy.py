from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Policy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reglement(self, ctx, titre, texte, role: discord.Role = None, image="aucun", emoji="aucun", texte_bouton="Accepter"):
        guild_id = ctx.guild.id
        role_id = role.id if role else None

        # Sauvegarde dans la DB
        self.bot.db.set_rule(guild_id, titre, texte, role_id, texte_bouton, emoji)

        # Message de confirmation
        msg = f"📜 Règlement configuré : **{titre}**\n{texte}\n"
        if role:
            msg += f"Rôle à attribuer : {role.mention}\n"
        if image != "aucun":
            msg += f"Image : {image}\n"
        msg += f"Texte du bouton : {texte_bouton}\nEmoji : {emoji}"
        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(Policy(bot))
