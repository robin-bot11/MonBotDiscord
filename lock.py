from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock_roles = []

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def setlock(self, ctx, *roles: discord.Role):
        self.lock_roles = roles
        noms = ", ".join([r.name for r in roles])
        await ctx.send(embed=discord.Embed(description=f"Rôles configurés pour le lock : {noms}", color=COLOR))

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        targets = channel.guild.channels if channel is None else [channel]
        for ch in targets:
            for role in self.lock_roles:
                await ch.set_permissions(role, send_messages=False, add_reactions=False, attach_files=False, use_external_emojis=False)
        nom = "tout le serveur" if channel is None else channel.name
        await ctx.send(embed=discord.Embed(description=f"{nom} est maintenant verrouillé pour les rôles configurés.", color=COLOR))

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        targets = channel.guild.channels if channel is None else [channel]
        for ch in targets:
            for role in self.lock_roles:
                await ch.set_permissions(role, send_messages=True, add_reactions=True, attach_files=True, use_external_emojis=True)
        nom = "tout le serveur" if channel is None else channel.name
        await ctx.send(embed=discord.Embed(description=f"{nom} est maintenant déverrouillé pour les rôles configurés.", color=COLOR))

def setup(bot):
    bot.add_cog(Lock(bot))
