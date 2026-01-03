from discord.ext import commands
import discord
import asyncio
import traceback

OWNER_ID = 1383790178522370058
COLOR = 0x6b00cb

class Creator(commands.Cog):
    """Toutes les commandes Owner, sécurisées et stables"""

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
        await self.safe_send(ctx, "✅ Le bot est en ligne.")

    @commands.command()
    async def dm(self, ctx, user_id: int, *, message):
        if not await self.check_owner(ctx): return
        try:
            user = await self.bot.fetch_user(user_id)
            await user.send(message)
            await self.safe_send(ctx, f"Message envoyé à {user}.")
        except discord.Forbidden:
            await self.safe_send(ctx, "❌ Impossible d'envoyer le message.")

    # ------------------ CONFIG ------------------
    @commands.command()
    async def backupconfig(self, ctx):
        if not await self.check_owner(ctx): return
        self.bot.db.backup()
        await self.safe_send(ctx, "💾 Configuration sauvegardée.")

    @commands.command()
    async def restoreconfig(self, ctx):
        if not await self.check_owner(ctx): return
        self.bot.db.restore()
        await self.safe_send(ctx, "💾 Configuration restaurée.")

    @commands.command()
    async def resetwarns(self, ctx, member_id: int):
        if not await self.check_owner(ctx): return
        guild_id = str(ctx.guild.id)
        self.bot.db.data.get("warns", {}).get(guild_id, {}).pop(str(member_id), None)
        self.bot.db.save()
        await self.safe_send(ctx, f"⚠️ Warns supprimés pour {member_id} sur ce serveur.")

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
            await self.safe_send(ctx, f"Salon {channel.name} | Type={channel.type}")
        else:
            await self.safe_send(ctx, "❌ Salon introuvable.")

    @commands.command()
    async def checkmember(self, ctx, member_id: int):
        if not await self.check_owner(ctx): return
        member = ctx.guild.get_member(member_id)
        if not member:
            return await self.safe_send(ctx, "❌ Membre introuvable.")
        roles = [r.name for r in member.roles if r.name != "@everyone"]
        await self.safe_send(ctx, f"Membre {member} | Rôles={roles}")

    # ------------------ LISTES ------------------
    @commands.command()
    async def listbots(self, ctx):
        if not await self.check_owner(ctx): return
        bots = [m.name for m in ctx.guild.members if m.bot]
        await self.safe_send(ctx, f"Bots : {', '.join(bots)}")

    @commands.command()
    async def servers(self, ctx, page: int = 1):
        if not await self.check_owner(ctx): return
        per_page = 5
        guilds = self.bot.guilds
        start = (page - 1) * per_page
        msg = "\n".join(f"{g.name} | {g.id}" for g in guilds[start:start+per_page])
        await self.safe_send(ctx, msg, dm=True)

    # ------------------ INVITE ------------------
    @commands.command()
    async def invite(self, ctx, guild_id: int):
        if not await self.check_owner(ctx): return
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return await self.safe_send(ctx, "❌ Serveur introuvable.", dm=True)

        bot_member = guild.members.me
        channel = next(
            (c for c in guild.text_channels if c.permissions_for(bot_member).create_instant_invite),
            None
        )

        if not channel:
            return await self.safe_send(ctx, "❌ Aucun salon valide.", dm=True)

        invite = await channel.create_invite(max_age=3600, max_uses=1)
        await self.safe_send(ctx, f"Invitation : {invite}", dm=True)

    # ------------------ SYSTEM ------------------
    @commands.command()
    async def shutdownbot(self, ctx):
        if not await self.check_owner(ctx): return
        await self.safe_send(ctx, "Arrêt du bot.", dm=True)
        await self.bot.close()

    @commands.command()
    async def restartbot(self, ctx):
        if not await self.check_owner(ctx): return
        await self.safe_send(ctx, "Redémarrage du bot.", dm=True)
        await self.bot.close()

    # ------------------ EVAL ------------------
    @commands.command()
    async def eval(self, ctx, *, code):
        if not await self.check_owner(ctx): return
        env = {"bot": self.bot, "ctx": ctx, "discord": discord}
        try:
            result = eval(code, env)
            if asyncio.iscoroutine(result):
                result = await result
            await self.safe_send(ctx, f"{result}", dm=True)
        except Exception:
            await self.safe_send(ctx, f"❌ Erreur :\n```{traceback.format_exc()}```", dm=True)

async def setup(bot):
    await bot.add_cog(Creator(bot))
