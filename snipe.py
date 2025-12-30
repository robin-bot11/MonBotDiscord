import discord
from discord.ext import commands

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.snipes = {}  # {guild_id: {channel_id: last_deleted_message}}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        guild_snipes = self.snipes.setdefault(message.guild.id, {})
        guild_snipes[message.channel.id] = message

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def snipe(self, ctx):
        guild_snipes = self.snipes.get(ctx.guild.id, {})
        msg = guild_snipes.get(ctx.channel.id)
        if msg:
            embed = discord.Embed(
                description=msg.content, color=0x6b00cb
            )
            embed.set_author(name=str(msg.author), icon_url=msg.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Rien à sniper ici.")

def setup(bot):
    bot.add_cog(Snipe(bot))
