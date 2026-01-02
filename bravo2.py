import discord
from discord.ext import commands
from base_donnees import Database

class Bienvenue(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        guild_data = self.db.data.get("verification", {}).get(guild_id, {})
        isolation_role_id = guild_data.get("isolation_role")
        if isolation_role_id:
            role = member.guild.get_role(isolation_role_id)
            if role:
                try:
                    await member.add_roles(role, reason="Rôle d'isolation automatique")
                except discord.Forbidden:
                    pass

        # Optionnel: envoyer message de bienvenue dans un salon spécifique
        welcome_channel_id = guild_data.get("welcome_channel")
        if welcome_channel_id:
            channel = member.guild.get_channel(welcome_channel_id)
            if channel:
                await channel.send(f"Bienvenue {member.mention} !")

# ---------------- Setup ----------------
async def setup(bot):
    await bot.add_cog(Bienvenue(bot))
