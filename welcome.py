from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = None
        self.message = "Bienvenue {user} sur {server} !"

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcome(self, ctx, *, message):
        self.message = message
        await ctx.send(embed=discord.Embed(
            description="Message de bienvenue configuré.",
            color=COLOR
        ))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcomechannel(self, ctx, channel: discord.TextChannel):
        self.channel = channel
        await ctx.send(embed=discord.Embed(
            description=f"Salon défini : {channel.mention}",
            color=COLOR
        ))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if self.channel:
            msg = self.message.format(
                user=member.mention,
                server=member.guild.name,
                members=member.guild.member_count
            )
            await self.channel.send(msg)

def setup(bot):
    bot.add_cog(Welcome(bot))
