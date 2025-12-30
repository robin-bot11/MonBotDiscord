import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns = {}  # {guild_id: {user_id: [warns]}}

    # --- Ban / Deban ---
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f"{member} a été banni. Raison : {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def deban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        guild = ctx.guild
        await guild.unban(user)
        await ctx.send(f"{user} a été débanni.")

    # --- Kick ---
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f"{member} a été expulsé. Raison : {reason}")

    # --- Mute / Demute ---
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if role:
            await member.add_roles(role)
            await ctx.send(f"{member} a été mute.")
        else:
            await ctx.send("Le rôle Muted n'existe pas.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def demute(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if role:
            await member.remove_roles(role)
            await ctx.send(f"{member} a été démute.")
        else:
            await ctx.send("Le rôle Muted n'existe pas.")

    # --- Warn ---
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        guild_warns = self.warns.setdefault(ctx.guild.id, {})
        user_warns = guild_warns.setdefault(member.id, [])
        user_warns.append(reason or "Aucune raison fournie")
        await ctx.send(f"{member} a été warn. Raison : {reason}")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warnlist(self, ctx, member: discord.Member):
        guild_warns = self.warns.get(ctx.guild.id, {})
        user_warns = guild_warns.get(member.id, [])
        if not user_warns:
            await ctx.send(f"{member} n'a aucun warn.")
        else:
            msg = "\n".join(f"{i+1}. {w}" for i, w in enumerate(user_warns))
            await ctx.send(f"Warns de {member} :\n{msg}")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def clearwarns(self, ctx, member: discord.Member):
        guild_warns = self.warns.get(ctx.guild.id, {})
        if member.id in guild_warns:
            guild_warns.pop(member.id)
            await ctx.send(f"Les warns de {member} ont été réinitialisés.")
        else:
            await ctx.send(f"{member} n'a aucun warn.")

def setup(bot):
    bot.add_cog(Moderation(bot))
