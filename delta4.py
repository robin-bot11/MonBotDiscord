# delta4.py
from discord.ext import commands
import discord
import asyncio
import traceback

OWNER_ID = 1383790178522370058
COLOR = 0x6b00cb

class Creator(commands.Cog):
    """Cog Owner : gestion complète, debug, stats, contrôle bot et hot-reload."""

    def __init__(self, bot):
        self.bot = bot

    # ---------------- UTILITAIRES ----------------
    def is_owner(self, ctx):
        return ctx.author.id == OWNER_ID

    async def check_owner(self, ctx):
        if not self.is_owner(ctx):
            await ctx.send("⛔ Vous n'êtes pas autorisé à utiliser cette commande.")
            return False
        return True

    # ---------------- PING / TEST ----------------
    @commands.command()
    async def ping(self, ctx):
        if not await self.check_owner(ctx): return
        await ctx.send("✅ Le bot est en ligne et répond correctement.")

    # ---------------- DM / MESSAGE ----------------
    @commands.command()
    async def dm(self, ctx, user_id: int, *, message):
        if not await self.check_owner(ctx): return
        user = await self.bot.fetch_user(user_id)
        try:
            await user.send(message)
            await ctx.send(f"Message envoyé à {user}.")
        except discord.Forbidden:
            await ctx.send("❌ Impossible d'envoyer le message à cet utilisateur.")

    @commands.command()
    async def say(self, ctx, channel_id: int, *, message):
        if not await self.check_owner(ctx): return
        channel = ctx.guild.get_channel(channel_id)
        if not channel:
            return await ctx.send("❌ Salon introuvable.")
        await channel.send(message)
        await ctx.send(f"✅ Message envoyé dans {channel.mention}.")

    # ---------------- BACKUP / RESTORE ----------------
    @commands.command()
    async def backupconfig(self, ctx):
        if not await self.check_owner(ctx): return
        try:
            self.bot.db.backup()
            await ctx.send("💾 Configuration sauvegardée avec succès.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")

    @commands.command()
    async def restoreconfig(self, ctx):
        if not await self.check_owner(ctx): return
        try:
            self.bot.db.restore()
            await ctx.send("💾 Configuration restaurée avec succès.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")

    # ---------------- HOT-RELOAD / COGS ----------------
    @commands.command()
    async def reloadcog(self, ctx, cog: str):
        if not await self.check_owner(ctx): return
        try:
            if cog in self.bot.extensions:
                await self.bot.reload_extension(cog)
                await ctx.send(f"♻️ {cog} rechargé avec succès.")
            else:
                await ctx.send("❌ Cog non chargé.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")

    @commands.command()
    async def loadcog(self, ctx, cog: str):
        if not await self.check_owner(ctx): return
        try:
            await self.bot.load_extension(cog)
            await ctx.send(f"✅ {cog} chargé avec succès.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")

    @commands.command()
    async def unloadcog(self, ctx, cog: str):
        if not await self.check_owner(ctx): return
        try:
            await self.bot.unload_extension(cog)
            await ctx.send(f"🛑 {cog} déchargé avec succès.")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")

    # ---------------- STATUTS / ACTIVITÉS ----------------
    @commands.command()
    async def setstatus(self, ctx, status: str, *, text: str):
        """Changer le statut : online, idle, dnd, invisible"""
        if not await self.check_owner(ctx): return
        mapping = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "invisible": discord.Status.invisible
        }
        if status.lower() not in mapping:
            return await ctx.send("❌ Status invalide. Choix: online, idle, dnd, invisible")
        await self.bot.change_presence(status=mapping[status.lower()], activity=discord.Game(name=text))
        await ctx.send(f"✅ Statut changé : {status} | {text}")

    @commands.command()
    async def setactivity(self, ctx, type: str, *, text: str):
        """Changer l'activité : playing, watching, listening, competing"""
        if not await self.check_owner(ctx): return
        mapping = {
            "playing": discord.ActivityType.playing,
            "watching": discord.ActivityType.watching,
            "listening": discord.ActivityType.listening,
            "competing": discord.ActivityType.competing
        }
        if type.lower() not in mapping:
            return await ctx.send("❌ Type invalide. Choix: playing, watching, listening, competing")
        activity = discord.Activity(type=mapping[type.lower()], name=text)
        await self.bot.change_presence(activity=activity)
        await ctx.send(f"✅ Activité changée : {type} | {text}")

    # ---------------- CHECK / INFO ----------------
    @commands.command()
    async def checkmember(self, ctx, member_id: int):
        if not await self.check_owner(ctx): return
        member = ctx.guild.get_member(member_id)
        if not member: return await ctx.send("❌ Membre introuvable.")
        roles = [r.name for r in member.roles if r.name != "@everyone"]
        await ctx.send(f"Membre {member} : Rôles={roles}, Admin={member.guild_permissions.administrator}")

    @commands.command()
    async def checkrole(self, ctx, role_id: int):
        if not await self.check_owner(ctx): return
        role = ctx.guild.get_role(role_id)
        if not role: return await ctx.send("❌ Rôle introuvable.")
        perms = [p[0] for p in role.permissions if p[1]]
        await ctx.send(f"Rôle {role.name} : {perms}")

    @commands.command()
    async def checkchannel(self, ctx, channel_id: int):
        if not await self.check_owner(ctx): return
        channel = ctx.guild.get_channel(channel_id)
        if channel:
            await ctx.send(f"Salon {channel.name} | Type={channel.type} | NSFW={getattr(channel, 'is_nsfw', False)}")
        else:
            await ctx.send("❌ Salon introuvable.")

    @commands.command()
    async def listbots(self, ctx):
        if not await self.check_owner(ctx): return
        bots = [m.name for m in ctx.guild.members if m.bot]
        await ctx.send(f"Bots sur ce serveur : {', '.join(bots)}")

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
        await ctx.author.send(msg)

    # ---------------- MODÉRATION ----------------
    @commands.command()
    async def resetwarns(self, ctx, member_id: int):
        if not await self.check_owner(ctx): return
        self.bot.db.data["warns"].pop(str(member_id), None)
        self.bot.db.save()
        await ctx.send(f"⚠️ Tous les warns de {member_id} ont été supprimés.")

    @commands.command()
    async def massrole(self, ctx, role_id: int, action: str, *member_ids: int):
        if not await self.check_owner(ctx): return
        role = ctx.guild.get_role(role_id)
        if not role: return await ctx.send("❌ Rôle introuvable.")
        added, removed = [], []
        for mid in member_ids:
            member = ctx.guild.get_member(mid)
            if not member: continue
            if action.lower() == "add":
                await member.add_roles(role)
                added.append(member.name)
            elif action.lower() == "remove":
                await member.remove_roles(role)
                removed.append(member.name)
        await ctx.send(f"✅ Roles modifiés :\nAjoutés: {added}\nRetirés: {removed}")

    # ---------------- SHUTDOWN / RESTART / POWERON ----------------
    @commands.command()
    async def shutdownbot(self, ctx):
        if not await self.check_owner(ctx): return
        await ctx.send("⚠️ Arrêt du bot...")
        await self.bot.close()

    @commands.command()
    async def restartbot(self, ctx):
        if not await self.check_owner(ctx): return
        await ctx.send("⚠️ Redémarrage du bot...")
        await self.bot.close()

    @commands.command()
    async def poweron(self, ctx):
        if not await self.check_owner(ctx): return
        await ctx.send("✅ Services internes activés ou relancés.")

    # ---------------- EVAL / DEBUG ----------------
    @commands.command()
    async def eval(self, ctx, *, code):
        if not await self.check_owner(ctx): return
        try:
            result = eval(code)
            if asyncio.iscoroutine(result):
                result = await result
            await ctx.send(f"Résultat : {result}")
        except Exception:
            await ctx.send(f"❌ Erreur :\n```{traceback.format_exc()}```")

# ---------------- SETUP ----------------
async def setup(bot):
    await bot.add_cog(Creator(bot))
