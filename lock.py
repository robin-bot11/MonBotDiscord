from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.locked_roles = []

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlock(self, ctx, *role_ids: int):
        self.locked_roles = []
        for role_id in role_ids:
            role = ctx.guild.get_role(role_id)
            if role:
                self.locked_roles.append(role.id)
        await ctx.send(embed=discord.Embed(description="Rôles configurés pour le lock.", color=COLOR))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def lock(self, ctx):
        for role_id in self.locked_roles:
            role = ctx.guild.get_role(role_id)
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(role, send_messages=False)
        await ctx.send(embed=discord.Embed(description="Les rôles sélectionnés ont été verrouillés.", color=COLOR))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unlock(self, ctx):
        for role_id in self.locked_roles:
            role = ctx.guild.get_role(role_id)
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(role, send_messages=True)
        await ctx.send(embed=discord.Embed(description="Les rôles sélectionnés ont été déverrouillés.", color=COLOR))

def setup(bot):
    bot.add_cog(Lock(bot))
