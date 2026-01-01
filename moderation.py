from discord.ext import commands
import discord
from datetime import datetime

COLOR = 0x6b00cb

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns = {}  # stocke les warns par ID de membre : {id: [{"raison":..., "moderateur":..., "date":...}, ...]}

    # ------------------ KICK ------------------
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member_id: int, *, reason=None):
        guild = ctx.guild
        member = guild.get_member(member_id)
        if not member:
            return await ctx.send("Membre introuvable avec cet ID.")
        try:
            await member.send(f"Vous avez été expulsé de {guild.name}. Raison : {reason}")
        except:
            pass
        await member.kick(reason=reason)
        await ctx.send(f"J'ai expulsé {member.mention}. Raison : {reason}")

    # ------------------ BAN ------------------
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member_id: int, *, reason=None):
        guild = ctx.guild
        member = guild.get_member(member_id)
        if not member:
            return await ctx.send("Membre introuvable avec cet ID.")
        try:
            await member.send(f"Vous avez été banni de {guild.name}. Raison : {reason}")
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
        self.warns.setdefault(member_id, []).append({
            "raison": reason,
            "moderateur": ctx.author.name,
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        })
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
        data = self.warns.get(member_id, [])
        if not data:
            return await ctx.send(f"{member.display_name} n'a aucun avertissement.")
        msg = f"Warns de {member.display_name} :\n"
        for i, w in enumerate(data, start=1):
            msg += f"{i} - {w['raison']} - par {w['moderateur']} - {w['date']}\n"
        await ctx.send(msg)

    # ------------------ SUPPRIMER UN WARN ------------------
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def delwarn(self, ctx, member_id: int, warn_number: int):
        data = self.warns.get(member_id, [])
        if not data or warn_number > len(data) or warn_number < 1:
            return await ctx.send("Aucun warn correspondant trouvé.")
        removed = data.pop(warn_number - 1)
        await ctx.send(f"J'ai supprimé le warn {warn_number} de {removed['raison']} pour le membre {ctx.guild.get_member(member_id).mention}.")

def setup(bot):
    bot.add_cog(Moderation(bot))
