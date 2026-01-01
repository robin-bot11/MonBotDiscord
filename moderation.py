# moderation.py
from discord.ext import commands
import discord
from datetime import datetime
from database import Database

COLOR = 0x6b00cb

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()  # On utilise la base pour stocker les warns

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
        await ctx.send(f"J'ai expulsé {member.mention}. Raison : {reason}")

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
        await ctx.send(f"J'ai banni {member.mention}. Raison : {reason}")

    # ------------------ UNBAN ------------------
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def uban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"J'ai débanni {user}.")

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
        await ctx.send(f"J'ai mute {member.mention}. Raison : {reason}")

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
            await ctx.send(f"J'ai unmute {member.mention}.")
            try:
                await member.send(f"Vous avez été unmute sur {ctx.guild.name}.")
            except:
                pass
        else:
            await ctx.send("Le membre n'était pas mute.")

    # ------------------ WARN ------------------
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member_id: int, *, reason=None):
        member = ctx.guild.get_member(member_id)
        if not member:
            return await ctx.send("Membre introuvable avec cet ID.")
        date = datetime.utcnow().strftime("%Y-%m-%d")
        self.db.add_warn(member_id, reason, ctx.author.name, date)
        try:
            await member.send(f"Vous avez reçu un avertissement sur {ctx.guild.name}. Raison : {reason}")
        except:
            pass
        await ctx.send(f"J'ai averti {member.mention}. Raison : {reason}")

    # ------------------ LISTE DES WARNS ------------------
    @commands.command()
    async def warns(self, ctx, member_id: int):
        member = ctx.guild.get_member(member_id)
        if not member:
            return await ctx.send("Membre introuvable avec cet ID.")
        data = self.db.get_warns(member_id)
        if not data:
            return await ctx.send(f"{member.display_name} n'a aucun avertissement.")
        msg = f"Warns de {member.display_name} :\n"
        for i, w in enumerate(data, start=1):
            msg += f"{i} - {w['reason']} - par {w['staff']} - {w['date']}\n"
        await ctx.send(msg)

    # ------------------ SUPPRIMER UN WARN ------------------
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def delwarn(self, ctx, member_id: int, warn_number: int):
        success = self.db.del_warn(member_id, warn_number - 1)
        member = ctx.guild.get_member(member_id)
        if success:
            await ctx.send(f"J'ai supprimé le warn {warn_number} pour {member.mention}.")
        else:
            await ctx.send("Aucun warn correspondant trouvé.")

def setup(bot):
    bot.add_cog(Moderation(bot))
