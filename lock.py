from discord.ext import commands
import discord
from datetime import datetime

warns = {}

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_member(self, ctx):
        if not ctx.author.guild_permissions.administrator and ctx.author.id != 1383790178522370058:
            await ctx.send(embed=discord.Embed(
                description="Vous n'avez pas la permission nécessaire pour utiliser cette commande.",
                color=0x6b00cb
            ))
            return False
        return True

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member_id: int, *, reason=None):
        member = ctx.guild.get_member(member_id)
        if not member:
            await ctx.send("Membre introuvable.")
            return
        await member.kick(reason=reason)
        await ctx.send(embed=discord.Embed(
            description=f"{member.name} a été expulsé. Raison: {reason}",
            color=0x6b00cb
        ))

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member_id: int, *, reason=None):
        member = ctx.guild.get_member(member_id)
        if not member:
            await ctx.send("Membre introuvable.")
            return
        await member.ban(reason=reason)
        await ctx.send(embed=discord.Embed(
            description=f"{member.name} a été banni. Raison: {reason}",
            color=0x6b00cb
        ))

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def uban(self, ctx, member_id: int):
        member = await ctx.guild.fetch_member(member_id)
        await ctx.guild.unban(member)
        await ctx.send(embed=discord.Embed(
            description=f"{member} a été débanni.",
            color=0x6b00cb
        ))

def setup(bot):
    bot.add_cog(Moderation(bot))
