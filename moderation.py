from discord.ext import commands
import discord
from datetime import datetime, timedelta
from database import Database

COLOR = 0x6b00cb

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()  # Base pour stocker les warns

    # ------------------ KICK ------------------
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member_id: int, *, reason=None):
        member = ctx.guild.get_member(member_id)
        if not member:
            return await ctx.send("Membre introuvable avec cet ID.")
        try:
            await member.send(f"Vous avez été expulsé de {ctx.guild.name}. Raison : {reason}")
        except:
            pass
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} a été expulsé. Raison : {reason}")

    # ------------------ BAN ------------------
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member_id: int, *, reason=None):
        member = ctx.guild.get_member(member_id)
        if not member:
            return await ctx.send("Membre introuvable avec cet ID.")
        try:
            await member.send(f"Vous avez été banni de {ctx.guild.name}. Raison : {reason}")
        except:
            pass
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} a été banni. Raison : {reason}")

    # ------------------ UNBAN ------------------
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def uban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"{user} a été débanni.")

    # ------------------ MUTE ------------------
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member_id: int, *, reason=None):
        member = ctx.guild.get_member(member_id)
        if not member:
            return await ctx.send("Membre introuvable avec cet ID.")
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted")
            for ch in ctx.guild.channels:
                await ch.set_permissions(mute_role, send_messages=False, speak=False)
        await member.add_roles(mute_role, reason=reason)
        try:
            await member.send(f"Vous avez été mute sur {ctx.guild.name}. Raison : {reason}")
        except:
            pass
        await ctx.send(f"{member.mention} a été mute. Raison : {reason}")

    # ------------------ UNMUTE ------------------
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member_id: int):
        member = ctx.guild.get_member(member_id)
        if not member:
            return await ctx.send("Membre introuvable avec cet ID.")
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            try:
                await member.send(f"Vous avez été unmute sur {ctx.guild.name}.")
            except:
                pass
            await ctx.send(f"{member.mention} a été unmute.")
        else:
            await ctx.send("Le membre n'était pas mute.")

    # ------------------ TIMEOUT ------------------
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member_id: int, duration: int):
        """Met un membre en timeout (minutes, max 28 jours)"""
        member = ctx.guild.get_member(member_id)
        if not member:
            return await ctx.send("Membre introuvable avec cet ID.")
        
        if duration > 40320:  # 28 jours
            return await ctx.send("⛔ Durée maximale : 28 jours (40320 minutes).")
        
        until = discord.utils.utcnow() + timedelta(minutes=duration)
        try:
            await member.edit(timed_out_until=until)
            await ctx.send(f"{member.mention} est en timeout pour {duration} minutes.")
        except Exception as e:
            await ctx.send(f"Impossible de mettre en timeout : {e}")

    # ------------------ GIVE ROLE / TAKE ROLE ------------------
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def giverole(self, ctx, member_id: int, role_id: int):
        member = ctx.guild.get_member(member_id)
        role = ctx.guild.get_role(role_id)
        if not member or not role:
            return await ctx.send("Membre ou rôle introuvable avec ces IDs.")
        await member.add_roles(role)
        await ctx.send(f"Le rôle {role.name} a été donné à {member.mention}.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def takerole(self, ctx, member_id: int, role_id: int):
        member = ctx.guild.get_member(member_id)
        role = ctx.guild.get_role(role_id)
        if not member or not role:
            return await ctx.send("Membre ou rôle introuvable avec ces IDs.")
        await member.remove_roles(role)
        await ctx.send(f"Le rôle {role.name} a été retiré à {member.mention}.")

    # ------------------ WARN ------------------
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member_id: int, *, reason=None):
        member = ctx.guild.get_member(member_id)
        if not member:
            return await ctx.send("Membre introuvable avec cet ID.")
        date = datetime.utcnow().strftime("%Y-%m-%d")
        self.db.add_warn(ctx.guild.id, member_id, reason, ctx.author.name, date)
        try:
            await member.send(f"Vous avez reçu un avertissement sur {ctx.guild.name}. Raison : {reason}")
        except:
            pass
        await ctx.send(f"{member.mention} a été averti. Raison : {reason}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warns(self, ctx, member_id: int):
        member = ctx.guild.get_member(member_id)
        if not member:
            return await ctx.send("Membre introuvable avec cet ID.")
        data = self.db.get_warns(ctx.guild.id, member_id)
        if not data:
            return await ctx.send(f"{member.display_name} n'a aucun avertissement.")
        msg = f"Warns de {member.display_name} :\n"
        for i, w in enumerate(data, start=1):
            msg += f"{i} - {w['reason']} - par {w['staff']} - {w['date']}\n"
        await ctx.send(msg)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def unwarn(self, ctx, member_id: int, warn_number: int):
        success = self.db.del_warn(ctx.guild.id, member_id, warn_number - 1)
        member = ctx.guild.get_member(member_id)
        if success:
            await ctx.send(f"Le warn {warn_number} pour {member.mention} a été supprimé.")
        else:
            await ctx.send("Aucun warn correspondant trouvé.")

    # ------------------ PURGE ------------------
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"{len(deleted)} messages supprimés.", delete_after=5)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purgeall(self, ctx):
        deleted = await ctx.channel.purge()
        await ctx.send(f"Tous les messages du salon ont été supprimés.", delete_after=5)


# ------------------ Setup ------------------
async def setup(bot):
    await bot.add_cog(Moderation(bot))
