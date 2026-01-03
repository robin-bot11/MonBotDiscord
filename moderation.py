# moderation.py
from discord.ext import commands
import discord
from datetime import datetime, timedelta
from storx import Database
from logx import COLOR  # Utilisation de la couleur du cog log

MAX_TIMEOUT_MINUTES = 40320  # 28 jours

class Moderation(commands.Cog):
    """Cog modération complet avec logs automatiques"""

    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    # ---------------- UTIL ----------------
    async def send_mod_log(self, guild, title, member, moderator, reason=None, extra=None):
        """Envoie un log modération vers le cog Logx"""
        embed = discord.Embed(title=title, color=COLOR)
        embed.add_field(name="Member", value=member.mention, inline=False)
        embed.add_field(name="By", value=moderator.mention if moderator else "Unknown", inline=False)
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        if extra:
            for key, val in extra.items():
                embed.add_field(name=key, value=val, inline=False)
        log_cog = self.bot.get_cog("Logx")
        if log_cog:
            await log_cog.send_log(guild, "log_mod", embed)

    async def fetch_member(self, ctx, member_id):
        member = ctx.guild.get_member(member_id)
        if not member:
            await ctx.send("❌ Membre introuvable avec cet ID.")
        return member

    # ---------------- KICK ----------------
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member_id: int, *, reason: str = "Aucune raison"):
        member = await self.fetch_member(ctx, member_id)
        if not member:
            return
        try:
            await member.send(f"⚠️ Vous avez été expulsé de {ctx.guild.name}. Raison : {reason}")
        except:
            pass
        await member.kick(reason=reason)
        await ctx.send(f"✅ {member.mention} a été expulsé. Raison : {reason}")
        await self.send_mod_log(ctx.guild, "👢 Member kicked", member, ctx.author, reason)

    # ---------------- BAN ----------------
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member_id: int, *, reason: str = "Aucune raison"):
        member = await self.fetch_member(ctx, member_id)
        if not member:
            return
        try:
            await member.send(f"⚠️ Vous avez été banni de {ctx.guild.name}. Raison : {reason}")
        except:
            pass
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member.mention} a été banni. Raison : {reason}")
        await self.send_mod_log(ctx.guild, "🔨 Member banned", member, ctx.author, reason)

    # ---------------- UNBAN ----------------
    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ {user} a été débanni.")
        await self.send_mod_log(ctx.guild, "♻️ Member unbanned", user, ctx.author)

    # ---------------- MUTE ----------------
    @commands.command(name="mute")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member_id: int, *, reason: str = "Aucune raison"):
        member = await self.fetch_member(ctx, member_id)
        if not member:
            return
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted")
            for ch in ctx.guild.channels:
                try:
                    await ch.set_permissions(mute_role, send_messages=False, speak=False)
                except:
                    pass
        await member.add_roles(mute_role, reason=reason)
        try:
            await member.send(f"🔇 Vous avez été mute sur {ctx.guild.name}. Raison : {reason}")
        except:
            pass
        await ctx.send(f"✅ {member.mention} a été mute. Raison : {reason}")
        await self.send_mod_log(ctx.guild, "🔇 Member muted", member, ctx.author, reason)

    # ---------------- UNMUTE ----------------
    @commands.command(name="unmute")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member_id: int):
        member = await self.fetch_member(ctx, member_id)
        if not member:
            return
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role and mute_role in member.roles:
            await member.remove_roles(mute_role)
            try:
                await member.send(f"🔊 Vous avez été unmute sur {ctx.guild.name}.")
            except:
                pass
            await ctx.send(f"✅ {member.mention} a été unmute.")
            await self.send_mod_log(ctx.guild, "🔊 Member unmuted", member, ctx.author)
        else:
            await ctx.send("❌ Le membre n'était pas mute.")

    # ---------------- TIMEOUT ----------------
    @commands.command(name="timeout")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member_id: int, duration: int):
        member = await self.fetch_member(ctx, member_id)
        if not member:
            return
        if duration > MAX_TIMEOUT_MINUTES:
            return await ctx.send(f"⛔ Durée maximale : 28 jours ({MAX_TIMEOUT_MINUTES} minutes).")
        until = discord.utils.utcnow() + timedelta(minutes=duration)
        await member.edit(timed_out_until=until)
        await ctx.send(f"✅ {member.mention} est en timeout pour {duration} minutes.")
        await self.send_mod_log(ctx.guild, "⏱️ Member timed out", member, ctx.author, f"{duration} minutes")

    # ---------------- GIVER / TAKE ROLE ----------------
    @commands.command(name="giverole")
    @commands.has_permissions(manage_roles=True)
    async def giverole(self, ctx, member_id: int, role_id: int):
        member = await self.fetch_member(ctx, member_id)
        role = ctx.guild.get_role(role_id)
        if not member or not role:
            return await ctx.send("❌ Membre ou rôle introuvable.")
        await member.add_roles(role)
        await ctx.send(f"✅ Le rôle {role.name} a été donné à {member.mention}.")
        await self.send_mod_log(ctx.guild, "➕ Role given", member, ctx.author, extra={"Role": role.name})

    @commands.command(name="takerole")
    @commands.has_permissions(manage_roles=True)
    async def takerole(self, ctx, member_id: int, role_id: int):
        member = await self.fetch_member(ctx, member_id)
        role = ctx.guild.get_role(role_id)
        if not member or not role:
            return await ctx.send("❌ Membre ou rôle introuvable.")
        await member.remove_roles(role)
        await ctx.send(f"✅ Le rôle {role.name} a été retiré à {member.mention}.")
        await self.send_mod_log(ctx.guild, "➖ Role removed", member, ctx.author, extra={"Role": role.name})

    # ---------------- WARN / UNWARN ----------------
    @commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member_id: int, *, reason: str = "Aucune raison"):
        member = await self.fetch_member(ctx, member_id)
        if not member:
            return
        date = datetime.utcnow().strftime("%Y-%m-%d")
        self.db.add_warn(ctx.guild.id, member_id, reason, ctx.author.name, date)
        try:
            await member.send(f"⚠️ Vous avez reçu un avertissement sur {ctx.guild.name}. Raison : {reason}")
        except:
            pass
        await ctx.send(f"✅ {member.mention} a été averti. Raison : {reason}")
        await self.send_mod_log(ctx.guild, "⚠️ Member warned", member, ctx.author, reason)

    @commands.command(name="unwarn")
    @commands.has_permissions(manage_messages=True)
    async def unwarn(self, ctx, member_id: int, warn_number: int):
        success = self.db.del_warn(ctx.guild.id, member_id, warn_number - 1)
        member = await self.fetch_member(ctx, member_id)
        if success:
            await ctx.send(f"✅ Le warn {warn_number} pour {member.mention} a été supprimé.")
            await self.send_mod_log(ctx.guild, "❌ Warn removed", member, ctx.author, extra={"Warn Number": str(warn_number)})
        else:
            await ctx.send("❌ Aucun warn correspondant trouvé.")

    @commands.command(name="warns")
    @commands.has_permissions(manage_messages=True)
    async def warns(self, ctx, member_id: int):
        member = await self.fetch_member(ctx, member_id)
        if not member:
            return
        data = self.db.get_warns(ctx.guild.id, member_id)
        if not data:
            return await ctx.send(f"{member.display_name} n'a aucun avertissement.")
        msg = f"📋 Warns de {member.display_name} :\n"
        for i, w in enumerate(data, start=1):
            msg += f"{i} - {w['reason']} - par {w['staff']} - {w['date']}\n"
        await ctx.send(msg)

    # ---------------- PURGE ----------------
    @commands.command(name="purge")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"✅ {len(deleted)} messages supprimés.", delete_after=5)

    @commands.command(name="purgeall")
    @commands.has_permissions(manage_messages=True)
    async def purgeall(self, ctx):
        deleted = await ctx.channel.purge()
        await ctx.send("✅ Tous les messages du salon ont été supprimés.", delete_after=5)

# ---------------- SETUP ----------------
async def setup(bot):
    await bot.add_cog(Moderation(bot))
