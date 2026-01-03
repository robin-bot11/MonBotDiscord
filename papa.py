# papa.py
import discord
from discord.ext import commands
import asyncio
import traceback
import psutil
import os
import time

OWNER_ID = 1383790178522370058
COLOR = 0x6b00cb
SNIPE_EXPIRATION = 86400  # 24h pour expiration snipes

class Owner(commands.Cog):
    """Toutes les commandes Owner/Créateur, incluant le contrôle des snipes"""

    def __init__(self, bot):
        self.bot = bot
        self.locked = False

    # ---------------- UTIL ----------------
    def is_owner(self, ctx):
        return ctx.author.id == OWNER_ID

    async def check_owner(self, ctx):
        if not self.is_owner(ctx):
            await ctx.send("⛔ Vous n'êtes pas autorisé à utiliser cette commande.")
            return False
        return True

    async def safe_send(self, ctx, content=None, embed=None, dm=False):
        try:
            if dm:
                if embed:
                    await ctx.author.send(embed=embed)
                else:
                    await ctx.author.send(content)
            else:
                if embed:
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(content)
        except discord.Forbidden:
            pass

    async def cog_check(self, ctx):
        if self.locked and not self.is_owner(ctx):
            await ctx.send("⛔ Le bot est actuellement verrouillé.")
            return False
        return True

    # ---------------- COMMANDES DE BASE ----------------
    @commands.command(name="owner_ping", help="Ping du bot (Owner) | Exemple : +owner_ping")
    async def owner_ping(self, ctx):
        if not await self.check_owner(ctx): return
        await self.safe_send(ctx, "✅ Le bot est en ligne.")

    @commands.command(name="owner_dm", help="Envoyer un DM [ID obligatoire] (Owner) | Exemple : +owner_dm 123456789012345678 Salut !")
    async def owner_dm(self, ctx, user_id: int, *, message):
        if not await self.check_owner(ctx): return
        try:
            user = await self.bot.fetch_user(user_id)
            await user.send(message)
            await self.safe_send(ctx, f"Message envoyé à {user}.")
        except discord.Forbidden:
            await self.safe_send(ctx, "❌ Impossible d'envoyer le message.")

    # ---------------- CONFIG ----------------
    @commands.command(name="owner_backupconfig", help="Sauvegarder la config | Exemple : +owner_backupconfig")
    async def owner_backupconfig(self, ctx):
        if not await self.check_owner(ctx): return
        self.bot.db.backup()
        await self.safe_send(ctx, "💾 Configuration sauvegardée.")

    @commands.command(name="owner_restoreconfig", help="Restaurer la config | Exemple : +owner_restoreconfig")
    async def owner_restoreconfig(self, ctx):
        if not await self.check_owner(ctx): return
        self.bot.db.restore()
        await self.safe_send(ctx, "💾 Configuration restaurée.")

    # ---------------- SNIPES OWNER ----------------
    @commands.command(name="owner_snipe_clear", help="Purge un snipe salon ou global [ID salon optionnel] | Exemple : +owner_snipe_clear 123456789012345678 ou +owner_snipe_clear")
    async def owner_snipe_clear(self, ctx, channel_id: int = None):
        if not await self.check_owner(ctx): return
        if channel_id:
            removed = self.bot.db.data.get("snipes", {}).pop(str(channel_id), None)
            self.bot.db.save()
            await self.safe_send(ctx, f"✅ Snipe du salon {channel_id} supprimé." if removed else "❌ Aucun snipe trouvé pour ce salon.")
        else:
            self.bot.db.data["snipes"] = {}
            self.bot.db.save()
            await self.safe_send(ctx, "🧹 Tous les snipes ont été purgés globalement.")

    @commands.command(name="owner_snipe_expire", help="Supprime les snipes expirés >24h | Exemple : +owner_snipe_expire")
    async def owner_snipe_expire(self, ctx):
        if not await self.check_owner(ctx): return
        snipes = self.bot.db.data.get("snipes", {})
        now = int(time.time())
        removed = 0
        for channel_id in list(snipes.keys()):
            if now - snipes[channel_id]["timestamp"] > SNIPE_EXPIRATION:
                del snipes[channel_id]
                removed += 1
        self.bot.db.save()
        await self.safe_send(ctx, f"🕑 Snipes expirés supprimés : {removed}")

    # ---------------- SYSTEM ----------------
    @commands.command(name="owner_shutdown", help="Arrêter le bot | Exemple : +owner_shutdown")
    async def owner_shutdown(self, ctx):
        if not await self.check_owner(ctx): return
        await self.safe_send(ctx, "⚠️ Arrêt du bot...", dm=True)
        await self.bot.close()

    @commands.command(name="owner_restart", help="Redémarrer le bot | Exemple : +owner_restart")
    async def owner_restart(self, ctx):
        if not await self.check_owner(ctx): return
        await self.safe_send(ctx, "⚠️ Redémarrage du bot...", dm=True)
        await self.bot.close()

    # ---------------- EVAL ----------------
    @commands.command(name="owner_eval", help="Évaluer du code Python | Exemple : +owner_eval 1+1")
    async def owner_eval(self, ctx, *, code):
        if not await self.check_owner(ctx): return
        env = {"bot": self.bot, "ctx": ctx, "discord": discord}
        try:
            result = eval(code, env)
            if asyncio.iscoroutine(result):
                result = await result
            await self.safe_send(ctx, f"{result}", dm=True)
        except Exception:
            await self.safe_send(ctx, f"❌ Erreur :\n```{traceback.format_exc()}```", dm=True)

    # ---------------- AUTRES COMMANDES ----------------
    @commands.command(name="owner_lock", help="Verrouiller le bot | Exemple : +owner_lock")
    async def owner_lock(self, ctx):
        if not await self.check_owner(ctx): return
        self.locked = True
        await self.safe_send(ctx, "🔒 Le bot est maintenant verrouillé.")

    @commands.command(name="owner_unlock", help="Déverrouiller le bot | Exemple : +owner_unlock")
    async def owner_unlock(self, ctx):
        if not await self.check_owner(ctx): return
        self.locked = False
        await self.safe_send(ctx, "🔓 Le bot est maintenant déverrouillé.")

    @commands.command(name="owner_status", help="Changer le statut du bot | Exemple : +owner_status online Joueur de test")
    async def owner_status(self, ctx, type: str, *, text: str):
        if not await self.check_owner(ctx): return
        types = {"online": discord.Status.online, "dnd": discord.Status.dnd,
                 "idle": discord.Status.idle, "invisible": discord.Status.invisible}
        status = types.get(type.lower())
        if not status:
            return await self.safe_send(ctx, "❌ Type invalide. Options: online, dnd, idle, invisible")
        await self.bot.change_presence(activity=discord.Game(name=text), status=status)
        await self.safe_send(ctx, f"✅ Statut changé en {type} | {text}")

    @commands.command(name="owner_reload", help="Recharger un cog [Nom du cog] | Exemple : +owner_reload Snipe")
    async def owner_reload(self, ctx, cog: str):
        if not await self.check_owner(ctx): return
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await self.safe_send(ctx, f"✅ Cog {cog} rechargé.")
        except Exception as e:
            await self.safe_send(ctx, f"❌ Erreur : {e}")

    @commands.command(name="owner_reloadall", help="Recharger tous les cogs | Exemple : +owner_reloadall")
    async def owner_reloadall(self, ctx):
        if not await self.check_owner(ctx): return
        reloaded = []
        for ext in list(self.bot.cogs.keys()):
            try:
                await self.bot.reload_extension(f"cogs.{ext}")
                reloaded.append(ext)
            except:
                continue
        await self.safe_send(ctx, f"✅ Cogs rechargés : {', '.join(reloaded)}")

    @commands.command(name="owner_botinfo", help="Infos du bot | Exemple : +owner_botinfo")
    async def owner_botinfo(self, ctx):
        if not await self.check_owner(ctx): return
        mem = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        await self.safe_send(ctx, f"Bot : {self.bot.user}\nServeurs : {len(self.bot.guilds)}\nLatence : {round(self.bot.latency*1000)}ms\nMémoire : {mem:.2f}MB")

    @commands.command(name="owner_latency", help="Latence du bot | Exemple : +owner_latency")
    async def owner_latency(self, ctx):
        if not await self.check_owner(ctx): return
        await self.safe_send(ctx, f"Latence : {round(self.bot.latency*1000)}ms")

    @commands.command(name="owner_memory", help="Mémoire du bot | Exemple : +owner_memory")
    async def owner_memory(self, ctx):
        if not await self.check_owner(ctx): return
        mem = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        await self.safe_send(ctx, f"Utilisation mémoire : {mem:.2f}MB")

    @commands.command(name="owner_leaveserver", help="Quitter un serveur [ID obligatoire] | Exemple : +owner_leaveserver 123456789012345678")
    async def owner_leaveserver(self, ctx, guild_id: int):
        if not await self.check_owner(ctx): return
        guild = self.bot.get_guild(guild_id)
        if guild:
            await guild.leave()
            await self.safe_send(ctx, f"✅ Le bot a quitté {guild.name}")
        else:
            await self.safe_send(ctx, "❌ Serveur introuvable.")

    # ---------------- HELP PAPA ----------------
    @commands.command(name="help.papa", help="Affiche toutes les commandes Owner/Créateur | Réservé au propriétaire")
    async def help_papa(self, ctx):
        if ctx.author.id != OWNER_ID:
            return await self.safe_send(ctx, "⛔ Cette commande est réservée au propriétaire @𝐃𝐄𝐔𝐒")
        embed = discord.Embed(title="💜 Aide Owner", color=COLOR)
        commands_list = [c for c in self.get_commands() if not c.hidden]
        description = ""
        for cmd in commands_list:
            description += f"**+{cmd.name}** : {cmd.help or 'Pas de description'}\n"
        embed.description = description
        await self.safe_send(ctx, embed=embed)

# ---------------- SETUP ----------------
async def setup(bot):
    await bot.add_cog(Owner(bot))
