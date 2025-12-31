from discord.ext import commands
import discord

class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel):
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"{channel.mention} est maintenant verrouillé.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel):
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(f"{channel.mention} est maintenant déverrouillé.")

def setup(bot):
    bot.add_cog(Lock(bot))
