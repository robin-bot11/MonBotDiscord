# partnership.py
from discord.ext import commands
import discord
import re

COLOR = 0x6b00cb
OWNER_ID = 1383790178522370058

INVITE_REGEX = r"(?:discord\.gg|discordapp\.com\/invite)\/[a-zA-Z0-9]+"

class Partnership(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner(self, ctx):
        return ctx.author.id == OWNER_ID

    @commands.command()
    async def setpartnerrole(self, ctx, role: discord.Role):
        """Définir le rôle à ping pour les liens d'invitation (Owner seulement)."""
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé à utiliser cette commande.")
        self.bot.db.set_partner_role(ctx.guild.id, role.id)
        await ctx.send(f"Rôle de partenariat défini : {role.mention}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # Vérifier si message contient un lien Discord
        if re.search(INVITE_REGEX, message.content):
            guild_id = message.guild.id
            role_id = self.bot.db.get_partner_role(guild_id)
            if role_id:
                role = message.guild.get_role(role_id)
                if role:
                    await message.channel.send(f"{role.mention} Un lien d'invitation a été posté !")

# Extension setup
async def setup(bot):
    # On ajoute deux méthodes à la base si elles n'existent pas
    if not hasattr(bot.db, "set_partner_role"):
        def set_partner_role(guild_id, role_id):
            bot.db.data.setdefault("partner_roles", {})
            bot.db.data["partner_roles"][str(guild_id)] = role_id
            bot.db.save()
        bot.db.set_partner_role = set_partner_role

    if not hasattr(bot.db, "get_partner_role"):
        def get_partner_role(guild_id):
            return bot.db.data.get("partner_roles", {}).get(str(guild_id))
        bot.db.get_partner_role = get_partner_role

    await bot.add_cog(Partnership(bot))
