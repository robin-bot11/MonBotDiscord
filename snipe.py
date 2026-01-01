# snipe.py
from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_deleted = {}  # {guild_id: {channel_id: message}}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        guild_id = message.guild.id
        channel_id = message.channel.id
        if guild_id not in self.last_deleted:
            self.last_deleted[guild_id] = {}
        self.last_deleted[guild_id][channel_id] = message

    @commands.command()
    async def snipe(self, ctx):
        """Affiche le dernier message supprimé dans le salon."""
        guild_id = ctx.guild.id
        channel_id = ctx.channel.id

        if guild_id in self.last_deleted and channel_id in self.last_deleted[guild_id]:
            msg = self.last_deleted[guild_id][channel_id]
            embed = discord.Embed(
                title="Dernier message supprimé",
                description=f"**Auteur :** {msg.author}\n**Message :** {msg.content}",
                color=COLOR
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("Rien à afficher pour le moment dans ce salon !")

def setup(bot):
    bot.add_cog(Snipe(bot))
