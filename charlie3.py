# charlie3.py
from discord.ext import commands
import discord
from datetime import datetime
from storx import Database  # Pour récupérer les salons de logs dynamiquement

COLOR = 0x6b00cb

class Logs(commands.Cog):
    """Cog pour gérer tous les logs : rôles, timeout, warns"""

    def __init__(self, bot):
        self.bot = bot
        self.db = Database()  # Instance de la base pour les logs

    # --------------------------------------------------
    # UTILITAIRE
    # --------------------------------------------------
    async def send_log(self, guild: discord.Guild, log_type: str, embed: discord.Embed):
        """Envoie un embed dans le salon de logs configuré pour le type"""
        channel_id = self.db.get_log_channel(guild.id, log_type)
        if not channel_id:
            return
        channel = guild.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)

    # ==================================================
    # ROLES — AJOUT / RETRAIT
    # ==================================================
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        added_roles = [r for r in after.roles if r not in before.roles]
        removed_roles = [r for r in before.roles if r not in after.roles]

        if not added_roles and not removed_roles:
            return

        moderator = "Inconnu"
        async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update):
            if entry.target.id == after.id:
                moderator = entry.user
                break

        embed = discord.Embed(
            title="🎭 Mise à jour des rôles",
            color=COLOR,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Membre", value=after.mention, inline=False)

        if added_roles:
            embed.add_field(
                name="➕ Rôles ajoutés",
                value=", ".join(r.mention for r in added_roles),
                inline=False
            )

        if removed_roles:
            embed.add_field(
                name="➖ Rôles retirés",
                value=", ".join(r.name for r in removed_roles),
                inline=False
            )

        embed.add_field(
            name="Modérateur",
            value=moderator.mention if isinstance(moderator, discord.Member) else moderator,
            inline=False
        )

        await self.send_log(after.guild, "role", embed)

    # ==================================================
    # TIMEOUT (MODÉRATION)
    # ==================================================
    @commands.Cog.listener()
    async def on_member_update_timeout(self, before: discord.Member, after: discord.Member):
        if before.communication_disabled_until == after.communication_disabled_until:
            return

        async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update):
            if entry.target.id != after.id:
                continue

            if after.communication_disabled_until:
                embed = discord.Embed(
                    title="⏱️ Timeout appliqué",
                    color=COLOR,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Membre", value=after.mention, inline=False)
                embed.add_field(name="Modérateur", value=entry.user.mention, inline=False)
                embed.add_field(
                    name="Jusqu’au",
                    value=discord.utils.format_dt(after.communication_disabled_until, "F"),
                    inline=False
                )
                embed.add_field(name="Raison", value=entry.reason or "Aucune", inline=False)
            else:
                embed = discord.Embed(
                    title="🔓 Timeout retiré",
                    color=COLOR,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Membre", value=after.mention, inline=False)
                embed.add_field(name="Modérateur", value=entry.user.mention, inline=False)

            await self.send_log(after.guild, "mod", embed)
            break

    # ==================================================
    # WARN (via audit logs / raison)
    # ==================================================
    async def log_warn(self, guild: discord.Guild, member: discord.Member, moderator: discord.Member, reason: str):
        """⚠️ Logger un warn (appelé depuis la commande +warn)"""
        embed = discord.Embed(
            title="⚠️ Avertissement",
            color=COLOR,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Membre", value=member.mention, inline=False)
        embed.add_field(name="Modérateur", value=moderator.mention, inline=False)
        embed.add_field(name="Raison", value=reason or "Aucune", inline=False)
        await self.send_log(guild, "mod", embed)

# --------------------------------------------------
# SETUP
# --------------------------------------------------
async def setup(bot):
    await bot.add_cog(Logs(bot))
