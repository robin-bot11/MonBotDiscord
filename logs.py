from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels = {}

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlog(self, ctx, log_type: str, channel: discord.TextChannel):
        log_types = ["role", "mod", "voice", "channel", "message", "member"]
        if log_type not in log_types:
            await ctx.send(embed=discord.Embed(description=f"Type invalide. Types possibles: {', '.join(log_types)}", color=COLOR))
            return
        self.channels[log_type] = channel
        await ctx.send(embed=discord.Embed(description=f"Salon de log pour {log_type} configuré : {channel.mention}", color=COLOR))

    # Exemple de listener pour messages supprimés
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        if "message" in self.channels:
            await self.channels["message"].send(embed=discord.Embed(
                description=f"Message supprimé de {message.author} dans {message.channel} :\n{message.content}",
                color=COLOR
            ))

def setup(bot):
    bot.add_cog(Logs(bot))
