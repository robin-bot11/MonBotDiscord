import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.text_channels, name="général")  # Mettre le salon par défaut
        if channel:
            embed = discord.Embed(
                description=f"Souhaitez la bienvenue à {member.mention} sur **{member.guild.name} !**\nNous sommes maintenant {member.guild.member_count} sur le serveur !!",
                color=0x6b00cb
            )
            await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Welcome(bot))
