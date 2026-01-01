from discord.ext import commands
import discord
from database import Database

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.welcome_channel = {}  # {guild_id: channel_id}

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcomechannel(self, ctx, channel: discord.TextChannel):
        """Configurer le salon pour le message de bienvenue"""
        guild_id = str(ctx.guild.id)
        self.welcome_channel[guild_id] = channel.id
        self.db.set_welcome_channel(guild_id, channel.id)
        await ctx.send(f"✅ Salon de bienvenue défini : {channel.mention}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        channel_id = self.welcome_channel.get(guild_id) or self.db.get_welcome_channel(guild_id)

        if not channel_id:
            return

        channel = member.guild.get_channel(channel_id)
        if channel:
            msg = (
                f"Souhaitez la bienvenue à {member.mention} sur **{member.guild.name} !**\n"
                f"Nous sommes maintenant {member.guild.member_count} sur le serveur !!"
            )
            await channel.send(msg)

def setup(bot):
    bot.add_cog(Welcome(bot))
