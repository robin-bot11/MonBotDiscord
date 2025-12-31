from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(embed=discord.Embed(
            description=f"{member} banni.",
            color=COLOR
        ))

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def uban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(embed=discord.Embed(
            description=f"{user} débanni.",
            color=COLOR
        ))

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(embed=discord.Embed(
            description=f"{member} expulsé.",
            color=COLOR
        ))

def setup(bot):
    bot.add_cog(Moderation(bot))
