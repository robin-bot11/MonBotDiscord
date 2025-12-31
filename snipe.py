from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last = None

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot:
            self.last = message

    @commands.command()
    async def snipe(self, ctx):
        if not self.last:
            return await ctx.send("Aucun message.")
        embed = discord.Embed(
            description=self.last.content,
            color=COLOR
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Snipe(bot))
