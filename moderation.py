from discord.ext import commands
import discord

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member_id: int, *, reason=None):
        member = await ctx.guild.fetch_member(member_id)
        await member.kick(reason=reason)
        await ctx.send(f"{member} a été expulsé. Raison : {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member_id: int, *, reason=None):
        member = await ctx.guild.fetch_member(member_id)
        await member.ban(reason=reason)
        await ctx.send(f"{member} a été banni. Raison : {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def uban(self, ctx, member_id: int):
        await ctx.guild.unban(discord.Object(id=member_id))
        await ctx.send(f"Membre {member_id} débanni.")

def setup(bot):
    bot.add_cog(Moderation(bot))
