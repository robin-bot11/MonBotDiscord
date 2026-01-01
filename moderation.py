from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.send(f"Vous avez été expulsé du serveur {ctx.guild.name}. Raison : {reason}")
        await member.kick(reason=reason)
        await ctx.send(f"J'ai expulsé {member.name}. Raison : {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.send(f"Vous avez été banni du serveur {ctx.guild.name}. Raison : {reason}")
        await member.ban(reason=reason)
        await ctx.send(f"J'ai banni {member.name}. Raison : {reason}")

def setup(bot):
    bot.add_cog(Moderation(bot))
