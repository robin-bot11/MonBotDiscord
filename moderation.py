from discord.ext import commands
import discord
from datetime import datetime

COLOR = 0x6b00cb

# Stockage temporaire des warns
warns = {}

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- Kick ---
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member_id: int, *, raison="Aucune raison fournie"):
        member = ctx.guild.get_member(member_id)
        if not member:
            await ctx.send(f"Membre introuvable avec l'ID {member_id}.")
            return
        try:
            await member.send(f"Vous avez été expulsé du serveur {ctx.guild.name} pour la raison : {raison}")
        except:
            pass
        await member.kick(reason=raison)
        await ctx.send(f"J’ai expulsé {member}.\nRaison : {raison}")

    # --- Ban ---
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member_id: int, *, raison="Aucune raison fournie"):
        member = ctx.guild.get_member(member_id)
        if not member:
            await ctx.send(f"Membre introuvable avec l'ID {member_id}.")
            return
        try:
            await member.send(f"Vous avez été banni du serveur {ctx.guild.name} pour la raison : {raison}")
        except:
            pass
        await member.ban(reason=raison)
        await ctx.send(f"J’ai banni {member}.\nMotif : {raison}")

    # --- Débannir ---
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def uban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        if not user:
            await ctx.send("Utilisateur introuvable.")
            return
        await ctx.guild.unban(user)
        await ctx.send(f"{user} a été débanni.")

    # --- Mute ---
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member_id: int, duree: str = None, *, raison="Aucune raison fournie"):
        member = ctx.guild.get_member(member_id)
        if not member:
            await ctx.send("Membre introuvable.")
            return
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted")
            for ch in ctx.guild.channels:
                await ch.set_permissions(mute_role, send_messages=False, speak=False)
        await member.add_roles(mute_role)
        try:
            await member.send(f"Vous avez été rendu muet sur {ctx.guild.name}. Raison : {raison}")
        except:
            pass
        await ctx.send(f"J’ai rendu muet {member}.\nMotif : {raison}")

    # --- Unmute ---
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def umute(self, ctx, member_id: int):
        member = ctx.guild.get_member(member_id)
        if not member:
            await ctx.send("Membre introuvable.")
            return
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            await ctx.send(f"{member} a été unmute.")
        else:
            await ctx.send(f"{member} n'était pas muet.")

    # --- Warn ---
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member_id: int, *, raison="Aucune raison fournie"):
        member = ctx.guild.get_member(member_id)
        if not member:
            await ctx.send("Membre introuvable.")
            return
        if member_id not in warns:
            warns[member_id] = []
        warns[member_id].append({"raison": raison, "mod": ctx.author.name, "date": datetime.now().strftime("%Y-%m-%d")})
        try:
            await member.send(f"Vous avez été averti sur {ctx.guild.name}. Raison : {raison}")
        except:
            pass
        await ctx.send(f"J’ai averti {member}.\nRaison : {raison}")

    # --- Liste Warns ---
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warns(self, ctx, member_id: int):
        member = ctx.guild.get_member(member_id)
        if not member:
            await ctx.send("Membre introuvable.")
            return
        if member_id not in warns or len(warns[member_id]) == 0:
            await ctx.send(f"{member} n'a aucun avertissement.")
            return
        msg = f"Warns de {member} :\n"
        for i, w in enumerate(warns[member_id], start=1):
            msg += f"{i} - {w['raison']} - par {w['mod']} - {w['date']}\n"
        await ctx.send(msg)

    # --- Supprimer un warn ---
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def delwarn(self, ctx, member_id: int, num: int):
        if member_id not in warns or len(warns[member_id]) < num or num <= 0:
            await ctx.send("Numéro de warn invalide.")
            return
        w = warns[member_id].pop(num-1)
        await ctx.send(f"Warn supprimé : {w['raison']}")

def setup(bot):
    bot.add_cog(Moderation(bot))
