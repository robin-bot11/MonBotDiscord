from discord.ext import commands
import discord
import asyncio
import traceback

OWNER_ID = 1383790178522370058
COLOR = 0x6b00cb

class Creator(commands.Cog):
    """Toutes les commandes Owner, sécurisées et hot reload safe"""

    def __init__(self, bot):
        self.bot = bot

    # ------------------ UTIL ------------------
    def is_owner(self, ctx):
        return ctx.author.id == OWNER_ID

    async def check_owner(self, ctx):
        if not self.is_owner(ctx):
            await ctx.send("⛔ Vous n'êtes pas autorisé à utiliser cette commande.")
            return False
        return True

    async def safe_send(self, ctx, content, dm=False):
        """Envoie le message dans le salon ou en DM si dm=True"""
        try:
            if dm:
                await ctx.author.send(content)
            else:
                await ctx.send(content)
        except discord.Forbidden:
            pass

    # ------------------ COMMANDES DE BASE ------------------
    @commands.command()
    async def ping(self, ctx):
        if not await self.check_owner(ctx): return
        await self.safe_send(ctx, "✅ Le bot est en ligne et répond correctement.")

    @commands.command()
    async def dm(self, ctx, user_id: int, *, message):
        if not await self.check_owner(ctx): return
        try:
            user = await self.bot.fetch_user(user_id)
            await user.send(message)
            await self.safe_send(ctx, f"Message envoyé à {user}.")
        except discord.Forbidden:
            await self.safe_send(ctx, "❌ Impossible d'envoyer le message.")

    # ------------------ CONFIGURATION ------------------
    @commands.command()
    async def backupconfig(self, ctx):
        if not await self.check_owner(ctx): return
        try:
            self.bot.db.backup()
            await self.safe_send(ctx, "💾 Configuration sauvegardée.")
        except Exception as e:
            await self.safe_send(ctx, f"❌ Erreur : {e}")

    @commands.command()
    async def restoreconfig(self, ctx):
        if not await self.check_owner(ctx): return
        try:
            self.bot.db.restore()
            await self.safe_send(ctx, "💾 Configuration restaurée.")
        except Exception as e:
            await self.safe_send(ctx, f"❌ Erreur : {e}")

    @commands.command()
    async def resetwarns(self, ctx, member_id: int):
        if not await self.check_owner(ctx): return
        self.bot.db.data["warns"].pop(str(member_id), None)
        self.bot.db.save()
        await self.safe_send(ctx, f"⚠️ Tous les warns de {member_id} ont été supprimés.")

    # ------------------ CHECK ------------------
    @commands.command()
    async def checkrole(self, ctx, role_id: int):
        if not await self.check_owner(ctx): return
        role = ctx.guild.get_role(role_id)
        if role:
            perms = [name for name, val in role.permissions if val]
            await self.safe_send(ctx, f"Rôle {role.name} : {perms}")
        else:
            await self.safe_send(ctx, "❌ Rôle introuvable.")

    @commands.command()
    async def checkchannel(self, ctx, channel_id: int):
        if not await self.check_owner(ctx): return
        channel = ctx.guild.get_channel(channel_id)
        if channel:
            await self.safe_send(ctx, f"Salon {channel.name} | Type={channel.type} | NSFW={getattr(channel, 'is_nsfw', False)}")
        else:
            await self.safe_send(ctx, "❌ Salon introuvable.")

    @commands.command()
    async def checkmember(self, ctx, member_id: int):
        if not await self.check_owner(ctx): return
        member = ctx.guild.get_member(member_id)
        if not member:
            return await self.safe_send(ctx, "❌ Membre introuvable.")
        roles = [r.name for r in member.roles if r.name != "@everyone"]
        await self.safe_send(ctx, f"Membre {member} : Rôles={roles}, Admin={member.guild_permissions.administrator}")

    # ------------------ LIST & SERVERS ------------------
    @commands.command()
    async def listbots(self, ctx):
        if not await self.check_owner(ctx): return
        bots = [m.name for m in ctx.guild.members if m.bot]
        await self.safe_send(ctx, f"Bots sur ce serveur : {', '.join(bots)}")

    @commands.command()
    async def servers(self, ctx, page: int = 1):
        if not await self.check_owner(ctx): return
        per_page = 5
        guilds = sorted(self.bot.guilds, key=lambda g: g.id, reverse=True)
        start = (page - 1) * per_page
        end = start + per_page
        msg = f"Serveurs (page {page}) :\n"
        for g in guilds[start:end]:
            msg += f"{g.name} | ID: {g.id} | Membres: {g.member_count}\n"
        await self.safe_send(ctx, msg, dm=True)  # Toujours en MP

    # ------------------ INVITE ------------------
    @commands.command()
    async def invite(self, ctx, guild_id: int):
        if not await self.check_owner(ctx): return
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return await self.safe_send(ctx, "❌ Serveur introuvable.", dm=True)
        channel = discord.utils.get(guild.text_channels, perms__create_instant_invite=True)
        if not channel:
            return await self.safe_send(ctx, "❌ Aucun salon disponible.", dm=True)
        invite = await channel.create_invite(max_age=3600, max_uses=1)
        await self.safe_send(ctx, f"Invitation pour {guild.name} : {invite}", dm=True)

    # ------------------ SHUTDOWN / RESTART ------------------
    @commands.command()
    async def shutdownbot(self, ctx):
        if not await self.check_owner(ctx): return
        await self.safe_send(ctx, "⚠️ Arrêt du bot...", dm=True)
        await self.bot.close()

    @commands.command()
    async def restartbot(self, ctx):
        if not await self.check_owner(ctx): return
        await self.safe_send(ctx, "⚠️ Redémarrage du bot...", dm=True)
        await self.bot.close()

    # ------------------ EVAL ------------------
    @commands.command()
    async def eval(self, ctx, *, code):
        if not await self.check_owner(ctx): return
        try:
            result = eval(code)
            if asyncio.iscoroutine(result):
                result = await result
            await self.safe_send(ctx, f"Résultat : {result}", dm=True)
        except Exception:
            await self.safe_send(ctx, f"❌ Erreur :\n```{traceback.format_exc()}```", dm=True)

# ------------------ Setup ------------------
async def setup(bot):
    await bot.add_cog(Creator(bot))
