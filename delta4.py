from discord.ext import commands
import discord
import asyncio
import traceback
import os
import psutil
import platform
from datetime import datetime

OWNER_ID = 1383790178522370058
COLOR = 0x6b00cb

class Creator(commands.Cog):
    """Toutes les commandes Owner, sécurisées et stables"""

    def __init__(self, bot):
        self.bot = bot
        self.locked = False  # lockbot / unlockbot

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

    # ------------------ GLOBAL CHECK ------------------
    @commands.Cog.listener()
    async def on_command(self, ctx):
        if self.locked and ctx.author.id != OWNER_ID:
            await ctx.send("🔒 Le bot est actuellement verrouillé.")
            ctx.command.reset_cooldown(ctx)
            return False

    # ------------------ BASE ------------------
    @commands.command()
    async def ping(self, ctx):
        if not await self.check_owner(ctx): return
        await self.safe_send(ctx, "✅ Le bot répond correctement.")

    @commands.command()
    async def latency(self, ctx):
        if not await self.check_owner(ctx): return
        await self.safe_send(ctx, f"🏓 Latence : `{round(self.bot.latency * 1000)}ms`")

    # ------------------ STATUS ------------------
    @commands.command()
    async def status(self, ctx, type: str, *, text: str):
        if not await self.check_owner(ctx): return

        types = {
            "playing": discord.ActivityType.playing,
            "watching": discord.ActivityType.watching,
            "listening": discord.ActivityType.listening,
            "competing": discord.ActivityType.competing
        }

        if type.lower() not in types:
            return await self.safe_send(
                ctx,
                "❌ Type invalide.\nTypes : playing / watching / listening / competing"
            )

        activity = discord.Activity(type=types[type.lower()], name=text)
        await self.bot.change_presence(activity=activity)
        await self.safe_send(ctx, f"✅ Statut mis à jour : **{type} {text}**")

    # ------------------ DM ------------------
    @commands.command()
    async def dm(self, ctx, user_id: int, *, message):
        if not await self.check_owner(ctx): return
        try:
            user = await self.bot.fetch_user(user_id)
            await user.send(message)
            await self.safe_send(ctx, f"📨 Message envoyé à {user}.")
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
        await self.safe_send(ctx, f"⚠️ Warns supprimés pour {member_id}.")

    # ------------------ CHECK ------------------
    @commands.command()
    async def checkrole(self, ctx, role_id: int):
        if not await self.check_owner(ctx): return
        role = ctx.guild.get_role(role_id)
        if not role:
            return await self.safe_send(ctx, "❌ Rôle introuvable.")
        perms = [p for p, v in role.permissions if v]
        await self.safe_send(ctx, f"🎭 **{role.name}**\nPermissions : {', '.join(perms)}")

    @commands.command()
    async def checkchannel(self, ctx, channel_id: int):
        if not await self.check_owner(ctx): return
        channel = ctx.guild.get_channel(channel_id)
        if not channel:
            return await self.safe_send(ctx, "❌ Salon introuvable.")
        await self.safe_send(ctx, f"📁 {channel.name} | Type : {channel.type}")

    @commands.command()
    async def checkmember(self, ctx, member_id: int):
        if not await self.check_owner(ctx): return
        member = ctx.guild.get_member(member_id)
        if not member:
            return await self.safe_send(ctx, "❌ Membre introuvable.")
        roles = [r.name for r in member.roles if r.name != "@everyone"]
        await self.safe_send(ctx, f"👤 {member}\nRôles : {roles}")

    # ------------------ LISTES ------------------
    @commands.command()
    async def listbots(self, ctx):
        if not await self.check_owner(ctx): return
        bots = [m.name for m in ctx.guild.members if m.bot]
        await self.safe_send(ctx, f"🤖 Bots : {', '.join(bots)}")

    @commands.command()
    async def servers(self, ctx):
        if not await self.check_owner(ctx): return
        msg = "\n".join(f"{g.name} | {g.id}" for g in self.bot.guilds)
        await self.safe_send(ctx, msg, dm=True)

    # ------------------ BOT INFO ------------------
    @commands.command()
    async def botinfo(self, ctx):
        if not await self.check_owner(ctx): return
        embed = discord.Embed(title="🤖 Bot Info", color=COLOR)
        embed.add_field(name="Serveurs", value=len(self.bot.guilds))
        embed.add_field(name="Utilisateurs", value=len(self.bot.users))
        embed.add_field(name="Python", value=platform.python_version())
        embed.add_field(name="Discord.py", value=discord.__version__)
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)

    @commands.command()
    async def memory(self, ctx):
        if not await self.check_owner(ctx): return
        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss / 1024 / 1024
        await self.safe_send(ctx, f"🧠 Mémoire utilisée : `{mem:.2f} MB`")

    # ------------------ SERVEUR ------------------
    @commands.command()
    async def leaveserver(self, ctx, guild_id: int):
        if not await self.check_owner(ctx): return
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return await self.safe_send(ctx, "❌ Serveur introuvable.")
        await guild.leave()
        await self.safe_send(ctx, f"🚪 Bot retiré de **{guild.name}**")

    # ------------------ LOCK ------------------
    @commands.command()
    async def lockbot(self, ctx):
        if not await self.check_owner(ctx): return
        self.locked = True
        await self.safe_send(ctx, "🔒 Bot verrouillé.")

    @commands.command()
    async def unlockbot(self, ctx):
        if not await self.check_owner(ctx): return
        self.locked = False
        await self.safe_send(ctx, "🔓 Bot déverrouillé.")

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

# ------------------ SETUP ------------------
async def setup(bot):
    await bot.add_cog(Creator(bot))
