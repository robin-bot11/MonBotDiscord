# verrouiller.py
from discord.ext import commands
import discord

class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock_roles = []

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def setlock(self, ctx, *roles: discord.Role):
        """Configure les rôles qui seront affectés par le lock"""
        self.lock_roles = roles
        if roles:
            noms = ", ".join([r.name for r in roles])
            await ctx.send(f"Les rôles suivants sont configurés pour le lock : {noms}")
        else:
            await ctx.send("Aucun rôle fourni. Les rôles de lock sont vides.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        """Verrouille un salon ou tous les salons pour les rôles configurés"""
        targets = ctx.guild.channels if channel is None else [channel]
        for ch in targets:
            for role in self.lock_roles:
                await ch.set_permissions(role, send_messages=False, add_reactions=False, attach_files=False, use_external_emojis=False)
        nom = "tout le serveur" if channel is None else channel.name
        roles_mention = ", ".join([role.mention for role in self.lock_roles])
        await ctx.send(f"{nom} est maintenant verrouillé pour les rôles : {roles_mention}")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        """Déverrouille un salon ou tous les salons pour les rôles configurés"""
        targets = ctx.guild.channels if channel is None else [channel]
        for ch in targets:
            for role in self.lock_roles:
                await ch.set_permissions(role, send_messages=True, add_reactions=True, attach_files=True, use_external_emojis=True)
        nom = "tout le serveur" if channel is None else channel.name
        roles_mention = ", ".join([role.mention for role in self.lock_roles])
        await ctx.send(f"{nom} est maintenant déverrouillé pour les rôles : {roles_mention}")

def setup(bot):
    bot.add_cog(Lock(bot))
