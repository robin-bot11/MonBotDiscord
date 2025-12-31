from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def papa(self, ctx):
        embed = discord.Embed(
            description="Mon papa est **𝐃𝐄𝐔𝐒**. Mon créateur. Mon maître.",
            color=COLOR
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Fun(bot))
