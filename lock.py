# logs.py
from discord.ext import commands
import discord
import asyncio

COLOR = 0x6b00cb

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------- UTIL ----------
    async def send_log(self, guild, log_type, embed):
        channel_id = self.bot.db.get_log_channel(guild.id, log_type)
        if not channel_id:
            return
        channel = guild.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)

    async def get_audit_user(self, guild, action, target_id=None):
        await asyncio.sleep(1)
        async for entry in guild.audit_logs(limit=5, action=action):
            if not target_id or (entry.target and entry.target.id == target_id):
                return entry.user, entry.reason
        return None, None

    # ---------- MESSAGE ----------
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.author.bot:
            return

        moderator, _ = await self.get_audit_user(
            message.guild,
            discord.AuditLogAction.message_delete,
            message.author.id
        )

        embed = discord.Embed(title="🗑️ Message supprimé", color=COLOR)
        embed.add_field(name="👤 Auteur", value=message.author, inline=False)
        embed.add_field(
            name="🛡️ Supprimé par",
            value=moderator or "Inconnu",
            inline=False
        )
        embed.add_field(name="📍 Salon", value=message.channel.mention, inline=False)
        embed.add_field(
            name="📝 Contenu",
            value=message.content or "*Embed / image / vide*",
            inline=False
        )

        await self.send_log(message.guild, "message", embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return

        embed = discord.Embed(title="✏️ Message édité", color=COLOR)
        embed.add_field(name="👤 Auteur", value=before.author, inline=False)
        embed.add_field(name="📍 Salon", value=before.channel.mention, inline=False)
        embed.add_field(name="Avant", value=before.content or "—", inline=False)
        embed.add_field(name="Après", value=after.content or "—", inline=False)

        await self.send_log(before.guild, "message", embed)

    # ---------- SALONS ----------
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        moderator, _ = await self.get_audit_user(
            channel.guild,
            discord.AuditLogAction.channel_create,
            channel.id
        )

        embed = discord.Embed(title="📁 Salon créé", color=COLOR)
        embed.add_field(name="Salon", value=channel.mention, inline=False)
        embed.add_field(name="Créé par", value=moderator or "Inconnu", inline=False)

        await self.send_log(channel.guild, "channel", embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        moderator, _ = await self.get_audit_user(
            channel.guild,
            discord.AuditLogAction.channel_delete,
            channel.id
        )

        embed = discord.Embed(title="🗑️ Salon supprimé", color=COLOR)
        embed.add_field(name="Salon", value=channel.name, inline=False)
        embed.add_field(name="Supprimé par", value=moderator or "Inconnu", inline=False)

        await self.send_log(channel.guild, "channel", embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        moderator, _ = await self.get_audit_user(
            after.guild,
            discord.AuditLogAction.channel_update,
            after.id
        )

        changes = []
        if before.name != after.name:
            changes.append(f"Nom : {before.name} → {after.name}")

        if not changes:
            return

        embed = discord.Embed(title="✏️ Salon modifié", color=COLOR)
        embed.add_field(name="Salon", value=after.mention, inline=False)
        embed.add_field(name="Modifié par", value=moderator or "Inconnu", inline=False)
        embed.add_field(name="Changements", value="\n".join(changes), inline=False)

        await self.send_log(after.guild, "channel", embed)

    # ---------- VOCAL ----------
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        embed = None

        if not before.channel and after.channel:
            embed = discord.Embed(
                title="🔊 Vocal rejoint",
                description=f"{member.mention} → {after.channel.mention}",
                color=COLOR
            )

        elif before.channel and not after.channel:
            embed = discord.Embed(
                title="🔇 Vocal quitté",
                description=f"{member.mention} ← {before.channel.name}",
                color=COLOR
            )

        elif before.channel and after.channel and before.channel != after.channel:
            embed = discord.Embed(
                title="🔁 Déplacement vocal",
                description=f"{member.mention}\n{before.channel.name} → {after.channel.name}",
                color=COLOR
            )

        if embed:
            await self.send_log(member.guild, "voice", embed)

    # ---------- MODÉRATION ----------
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        moderator, reason = await self.get_audit_user(
            guild,
            discord.AuditLogAction.ban,
            user.id
        )

        embed = discord.Embed(title="🔨 Membre banni", color=COLOR)
        embed.add_field(name="Membre", value=user, inline=False)
        embed.add_field(name="Modérateur", value=moderator or "Inconnu", inline=False)
        embed.add_field(name="Raison", value=reason or "Aucune", inline=False)

        await self.send_log(guild, "mod", embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        moderator, _ = await self.get_audit_user(
            member.guild,
            discord.AuditLogAction.kick,
            member.id
        )

        if not moderator:
            return

        embed = discord.Embed(title="👢 Membre expulsé", color=COLOR)
        embed.add_field(name="Membre", value=member, inline=False)
        embed.add_field(name="Modérateur", value=moderator, inline=False)

        await self.send_log(member.guild, "mod", embed)

    # ---------- RÔLES ----------
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles == after.roles:
            return

        moderator, _ = await self.get_audit_user(
            after.guild,
            discord.AuditLogAction.member_role_update,
            after.id
        )

        added = set(after.roles) - set(before.roles)
        removed = set(before.roles) - set(after.roles)

        if added:
            embed = discord.Embed(title="➕ Rôle ajouté", color=COLOR)
            embed.add_field(name="Membre", value=after.mention, inline=False)
            embed.add_field(
                name="Rôle",
                value=", ".join(r.name for r in added if r.name != "@everyone"),
                inline=False
            )
            embed.add_field(name="Par", value=moderator or "Inconnu", inline=False)
            await self.send_log(after.guild, "role", embed)

        if removed:
            embed = discord.Embed(title="➖ Rôle retiré", color=COLOR)
            embed.add_field(name="Membre", value=after.mention, inline=False)
            embed.add_field(
                name="Rôle",
                value=", ".join(r.name for r in removed if r.name != "@everyone"),
                inline=False
            )
            embed.add_field(name="Par", value=moderator or "Inconnu", inline=False)
            await self.send_log(after.guild, "role", embed)


async def setup(bot):
    await bot.add_cog(Logs(bot))
