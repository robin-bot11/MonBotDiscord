# verrouiller.py
from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock_roles = {}  # {guild_id: [role_ids]}

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlock(self, ctx, *roles: discord.Role):
        """Définir quels rôles seront affectés par le lock"""
        self.lock_roles[ctx.guild.id] = [r.id for r in roles]
        roles_names = ", ".join(r.name for r in roles)
        await ctx.send(embed=discord.Embed(
            description=f"Rôles verrouillés configurés : {roles_names}",
            color=COLOR
        ))

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel):
        """Verrouiller un salon pour les rôles configurés"""
        guild_id = ctx.guild.id
        if guild_id not in self.lock_roles:
            await ctx.send("Aucun rôle configuré pour le verrouillage. Utilisez +setlock.")
            return
        for role_id in self.lock_roles[guild_id]:
            role = ctx.guild.get_role(role_id)
            if role:
                await channel.set_permissions(role, send_messages=False, add_reactions=False, attach_files=False, embed_links=False)
        await ctx.send(embed=discord.Embed(
            description=f"{channel.mention} est maintenant verrouillé pour les rôles configurés.",
            color=COLOR
        ))

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel):
        """Déverrouiller un salon pour les rôles configurés"""
        guild_id = ctx.guild.id
        if guild_id not in self.lock_roles:
            await ctx.send("Aucun rôle configuré pour le verrouillage. Utilisez +setlock.")
            return
        for role_id in self.lock_roles[guild_id]:
            role = ctx.guild.get_role(role_id)
            if role:
                await channel.set_permissions(role, send_messages=True, add_reactions=True, attach_files=True, embed_links=True)
        await ctx.send(embed=discord.Embed(
            description=f"{channel.mention} est maintenant déverrouillé pour les rôles configurés.",
            color=COLOR
        ))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def lockserver(self, ctx):
        """Verrouiller tous les salons du serveur pour les rôles configurés"""
        guild_id = ctx.guild.id
        if guild_id not in self.lock_roles:
            await ctx.send("Aucun rôle configuré pour le verrouillage. Utilisez +setlock.")
            return
        for channel in ctx.guild.text_channels:
            for role_id in self.lock_roles[guild_id]:
                role = ctx.guild.get_role(role_id)
                if role:
                    await channel.set_permissions(role, send_messages=False, add_reactions=False, attach_files=False, embed_links=False)
        await ctx.send(embed=discord.Embed(
            description="Tous les salons ont été verrouillés pour les rôles configurés.",
            color=COLOR
        ))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unlockserver(self, ctx):
        """Déverrouiller tous les salons du serveur pour les rôles configurés"""
        guild_id = ctx.guild.id
        if guild_id not in self.lock_roles:
            await ctx.send("Aucun rôle configuré pour le verrouillage. Utilisez +setlock.")
            return
        for channel in ctx.guild.text_channels:
            for role_id in self.lock_roles[guild_id]:
                role = ctx.guild.get_role(role_id)
                if role:
                    await channel.set_permissions(role, send_messages=True, add_reactions=True, attach_files=True, embed_links=True)
        await ctx.send(embed=discord.Embed(
            description="Tous les salons ont été déverrouillés pour les rôles configurés.",
            color=COLOR
        ))

def setup(bot):
    bot.add_cog(Lock(bot))
