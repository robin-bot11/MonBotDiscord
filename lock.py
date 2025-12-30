from discord.ext import commands

class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def lock(self, ctx, channel: commands.TextChannel):
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"{channel.mention} est maintenant verrouillé.")

    @commands.command()
    async def unlock(self, ctx, channel: commands.TextChannel):
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(f"{channel.mention} est maintenant déverrouillé.")

def setup(bot):
    bot.add_cog(Lock(bot))
