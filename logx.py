from discord.ext import commands
import discord
import asyncio

COLOR = 0x6b00cb
SUCCESS_COLOR = 0x00ff00  # Vert pour confirmation

class Logx(commands.Cog):
    """Gestion complète des logs : messages, salons, vocaux, modérations, rôles, membres, warns et mutes."""

    def __init__(self, bot):
        self.bot = bot
        self.db = getattr(bot, "db", None)  # Accès sécurisé à la DB

    # -------------------- UTIL --------------------
    async def send_log(self, guild, log_type, embed):
        """Envoie l'embed dans le salon configuré"""
        if not self.db:
            return
        channel_id = self.db.get_log_channel(guild.id, log_type)
        if not channel_id:
            return
        channel = guild.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)

    async def get_audit_user(self, guild, action, target_id=None):
        """Récupère le modérateur et la raison depuis les audit logs"""
        await asyncio.sleep(1)
        try:
            async for entry in guild.audit_logs(limit=5, action=action):
                if not target_id or (entry.target and entry.target.id == target_id):
                    return entry.user, entry.reason
        except Exception:
            return None, None
        return None, None

    async def _set_log_channel(self, ctx, log_type, channel: discord.TextChannel):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("⛔ Tu dois être admin pour configurer les logs.")
        if not self.db:
            return await ctx.send("❌ La base de données n'est pas configurée.")
        self.db.set_log_channel(ctx.guild.id, log_type, channel.id)
        embed = discord.Embed(
            title=f"✅ {log_type} configuré",
            description=f"Les logs de type `{log_type}` seront envoyés dans {channel.mention}.",
            color=SUCCESS_COLOR
        )
        await ctx.send(embed=embed)

    # -------------------- COMMANDES CONFIG --------------------
    @commands.command(name="log_message")
    async def log_message(self, ctx, channel: discord.TextChannel):
        await self._set_log_channel(ctx, "log_message", channel)

    @commands.command(name="log_channel")
    async def log_channel(self, ctx, channel: discord.TextChannel):
        await self._set_log_channel(ctx, "log_channel", channel)

    @commands.command(name="log_vocal")
    async def log_vocal(self, ctx, channel: discord.TextChannel):
        await self._set_log_channel(ctx, "log_vocal", channel)

    @commands.command(name="log_mod")
    async def log_mod(self, ctx, channel: discord.TextChannel):
        await self._set_log_channel(ctx, "log_mod", channel)

    @commands.command(name="log_role")
    async def log_role(self, ctx, channel: discord.TextChannel):
        await self._set_log_channel(ctx, "log_role", channel)

    @commands.command(name="log_member")
    async def log_member(self, ctx, channel: discord.TextChannel):
        await self._set_log_channel(ctx, "log_member", channel)

    # -------------------- LISTENERS --------------------
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

    # -------------------- LOG MOD --------------------
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
        if moderator:
            embed = discord.Embed(title="👢 Member kicked", color=COLOR)
            embed.add_field(name="Member", value=member, inline=False)
            embed.add_field(name="Moderator", value=moderator, inline=False)
            await self.send_log(member.guild, "log_mod", embed)

    # -------------------- WARN / MUTE / DEMUTE --------------------
    async def log_warn(self, guild, member, moderator, reason):
        """Logger un warn"""
        embed = discord.Embed(title="⚠️ Member warned", color=COLOR)
        embed.add_field(name="Member", value=member, inline=False)
        embed.add_field(name="Moderator", value=moderator, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        await self.send_log(guild, "log_mod", embed)

    async def log_mute(self, guild, member, moderator, reason=None):
        """Logger un mute"""
        embed = discord.Embed(title="🔇 Member muted", color=COLOR)
        embed.add_field(name="Member", value=member, inline=False)
        embed.add_field(name="Moderator", value=moderator, inline=False)
        embed.add_field(name="Reason", value=reason or "None", inline=False)
        await self.send_log(guild, "log_mod", embed)

    async def log_demute(self, guild, member, moderator):
        """Logger un demute"""
        embed = discord.Embed(title="🔊 Member unmuted", color=COLOR)
        embed.add_field(name="Member", value=member, inline=False)
        embed.add_field(name="Moderator", value=moderator, inline=False)
        await self.send_log(guild, "log_mod", embed)

    # -------------------- LOG ROLES & MEMBERS --------------------
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
    await bot.add_cog(Logx(bot))
