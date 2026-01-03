# logx.py
from discord.ext import commands
import discord
import asyncio

COLOR = 0x6b00cb

class Logx(commands.Cog):
    """Cog for managing all logs: messages, channels, voice, moderation, and roles."""

    def __init__(self, bot):
        self.bot = bot
        self.db = getattr(bot, "db", None)  # Secure access to DB

    # -------------------- UTIL --------------------
    async def send_log(self, guild, log_type, embed):
        """Send the embed to the configured log channel"""
        if not self.db:
            return
        channel_id = self.db.get_log_channel(guild.id, log_type)
        if not channel_id:
            return
        channel = guild.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)

    async def get_audit_user(self, guild, action, target_id=None):
        """Get moderator and reason from audit logs"""
        await asyncio.sleep(1)  # Give Discord time to update audit logs
        async for entry in guild.audit_logs(limit=5, action=action):
            if not target_id or (entry.target and entry.target.id == target_id):
                return entry.user, entry.reason
        return None, None

    # -------------------- LOG MESSAGES --------------------
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.author.bot:
            return
        moderator, _ = await self.get_audit_user(message.guild, discord.AuditLogAction.message_delete, message.author.id)
        embed = discord.Embed(title="🗑️ Message deleted", color=COLOR)
        embed.add_field(name="Member", value=message.author, inline=False)
        embed.add_field(name="Deleted by", value=moderator or "Unknown", inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        embed.add_field(name="Content", value=message.content or "*Embed / file*", inline=False)
        await self.send_log(message.guild, "log_message", embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        embed = discord.Embed(title="✏️ Message edited", color=COLOR)
        embed.add_field(name="Member", value=before.author, inline=False)
        embed.add_field(name="Channel", value=before.channel.mention, inline=False)
        embed.add_field(name="Before", value=before.content or "—", inline=False)
        embed.add_field(name="After", value=after.content or "—", inline=False)
        await self.send_log(before.guild, "log_message", embed)

    # -------------------- LOG CHANNELS --------------------
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        moderator, _ = await self.get_audit_user(channel.guild, discord.AuditLogAction.channel_create, channel.id)
        embed = discord.Embed(title="📁 Channel created", color=COLOR)
        embed.add_field(name="Channel", value=channel.mention, inline=False)
        embed.add_field(name="Created by", value=moderator or "Unknown", inline=False)
        await self.send_log(channel.guild, "log_channel", embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        moderator, _ = await self.get_audit_user(channel.guild, discord.AuditLogAction.channel_delete, channel.id)
        embed = discord.Embed(title="🗑️ Channel deleted", color=COLOR)
        embed.add_field(name="Channel", value=channel.name, inline=False)
        embed.add_field(name="Deleted by", value=moderator or "Unknown", inline=False)
        await self.send_log(channel.guild, "log_channel", embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if before.name == after.name:
            return
        moderator, _ = await self.get_audit_user(after.guild, discord.AuditLogAction.channel_update, after.id)
        embed = discord.Embed(title="✏️ Channel updated", color=COLOR)
        embed.add_field(name="Channel", value=after.mention, inline=False)
        embed.add_field(name="Updated by", value=moderator or "Unknown", inline=False)
        embed.add_field(name="Name", value=f"{before.name} → {after.name}", inline=False)
        await self.send_log(after.guild, "log_channel", embed)

    # -------------------- LOG VOICE --------------------
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        embed = None
        if not before.channel and after.channel:
            embed = discord.Embed(title="🔊 Voice joined", description=f"{member.mention} → {after.channel.mention}", color=COLOR)
        elif before.channel and not after.channel:
            embed = discord.Embed(title="🔇 Voice left", description=f"{member.mention} ← {before.channel.mention}", color=COLOR)
        elif before.channel and after.channel and before.channel != after.channel:
            embed = discord.Embed(title="🔁 Voice moved", description=f"{member.mention}\n{before.channel.name} → {after.channel.name}", color=COLOR)
        if embed:
            await self.send_log(member.guild, "log_vocal", embed)

    # -------------------- LOG MODERATION --------------------
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        moderator, reason = await self.get_audit_user(guild, discord.AuditLogAction.ban, user.id)
        embed = discord.Embed(title="🔨 Member banned", color=COLOR)
        embed.add_field(name="Member", value=user, inline=False)
        embed.add_field(name="Moderator", value=moderator or "Unknown", inline=False)
        embed.add_field(name="Reason", value=reason or "None", inline=False)
        await self.send_log(guild, "log_mod", embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        moderator, _ = await self.get_audit_user(member.guild, discord.AuditLogAction.kick, member.id)
        if not moderator:
            return
        embed = discord.Embed(title="👢 Member kicked", color=COLOR)
        embed.add_field(name="Member", value=member, inline=False)
        embed.add_field(name="Moderator", value=moderator, inline=False)
        await self.send_log(member.guild, "log_mod", embed)

    # -------------------- LOG ROLES --------------------
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        moderator, _ = await self.get_audit_user(role.guild, discord.AuditLogAction.role_create, role.id)
        embed = discord.Embed(title="➕ Role created", color=COLOR)
        embed.add_field(name="Role", value=role.name, inline=False)
        embed.add_field(name="By", value=moderator or "Unknown", inline=False)
        await self.send_log(role.guild, "log_role", embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        moderator, _ = await self.get_audit_user(role.guild, discord.AuditLogAction.role_delete, role.id)
        embed = discord.Embed(title="➖ Role deleted", color=COLOR)
        embed.add_field(name="Role", value=role.name, inline=False)
        embed.add_field(name="By", value=moderator or "Unknown", inline=False)
        await self.send_log(role.guild, "log_role", embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        moderator, _ = await self.get_audit_user(after.guild, discord.AuditLogAction.role_update, after.id)
        embed = discord.Embed(title="✏️ Role updated", color=COLOR)
        embed.add_field(name="Role", value=f"{before.name} → {after.name}", inline=False)
        embed.add_field(name="By", value=moderator or "Unknown", inline=False)
        await self.send_log(after.guild, "log_role", embed)

    # -------------------- LOG MEMBER (nickname + roles) --------------------
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        moderator, _ = await self.get_audit_user(after.guild, discord.AuditLogAction.member_role_update, after.id)
        added = set(after.roles) - set(before.roles)
        removed = set(before.roles) - set(after.roles)

        if added:
            embed = discord.Embed(title="➕ Role added", color=COLOR)
            embed.add_field(name="Member", value=after.mention, inline=False)
            embed.add_field(name="Role", value=", ".join(r.name for r in added if r.name != "@everyone"), inline=False)
            embed.add_field(name="By", value=moderator or "Unknown", inline=False)
            await self.send_log(after.guild, "log_member", embed)

        if removed:
            embed = discord.Embed(title="➖ Role removed", color=COLOR)
            embed.add_field(name="Member", value=after.mention, inline=False)
            embed.add_field(name="Role", value=", ".join(r.name for r in removed if r.name != "@everyone"), inline=False)
            embed.add_field(name="By", value=moderator or "Unknown", inline=False)
            await self.send_log(after.guild, "log_member", embed)

        if before.display_name != after.display_name:
            embed = discord.Embed(title="✏️ Member nickname changed", color=COLOR)
            embed.add_field(name="Member", value=after.mention, inline=False)
            embed.add_field(name="Before", value=before.display_name, inline=False)
            embed.add_field(name="After", value=after.display_name, inline=False)
            embed.add_field(name="By", value=moderator or "Unknown", inline=False)
            await self.send_log(after.guild, "log_member", embed)

# -------------------- Setup --------------------
async def setup(bot):
    if "Logx" in bot.cogs:
        print("⚠️ Cog 'Logx' already loaded, setup skipped.")
        return
    await bot.add_cog(Logx(bot))
