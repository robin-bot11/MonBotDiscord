from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channels = {}

    @commands.command()
    async def setlog(self, ctx, log_type, channel: discord.TextChannel):
        self.log_channels[log_type] = channel.id
        embed = discord.Embed(
            description=f"Logs **{log_type}** configurés dans {channel.mention}",
            color=COLOR
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Logs(bot))
