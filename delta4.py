# delta4_pro.py
from discord.ext import commands
import discord
import asyncio
import traceback

OWNER_ID = 1383790178522370058
COLOR = 0x6b00cb

# ---------------- Cog principal ----------------
class Creator(commands.Cog):
    """Commandes réservées au propriétaire du bot (Owner)"""

    def __init__(self, bot):
        self.bot = bot

    # ---------------- Utilitaire ----------------
    def is_owner(self, ctx):
        return ctx.author.id == OWNER_ID

    async def check_owner(self, ctx):
        if not self.is_owner(ctx):
            await ctx.send(embed=discord.Embed(
                description="⛔ Vous n'êtes pas autorisé à utiliser cette commande.",
                color=COLOR
            ))
            return False
        return True

    async def safe_send(self, ctx, content=None, embed=None):
        try:
            if embed:
                await ctx.send(embed=embed)
            else:
                await ctx.send(content)
        except discord.Forbidden:
            pass

    # ---------------- Ping ----------------
    @commands.command()
    async def ping(self, ctx):
        if not await self.check_owner(ctx):
            return
        await self.safe_send(ctx, embed=discord.Embed(
            description="✅ Le bot est en ligne et répond correctement.",
            color=COLOR
        ))

    # ---------------- DM ----------------
    @commands.command()
    async def dm(self, ctx, user_id: int, *, message):
        if not await self.check_owner(ctx):
            return
        try:
            user = await self.bot.fetch_user(user_id)
            await user.send(message)
            await self.safe_send(ctx, f"✅ Message envoyé à {user}.")
        except discord.Forbidden:
            await self.safe_send(ctx, "❌ Impossible d'envoyer le message à cet utilisateur.")
        except Exception as e:
            await self.safe_send(ctx, f"❌ Erreur : {e}")

    # ---------------- Backup / Restore ----------------
    @commands.command()
    async def backupconfig(self, ctx):
        if not await self.check_owner(ctx):
            return
        try:
            self.bot.db.backup()
            await self.safe_send(ctx, "💾 Configuration sauvegardée avec succès.")
        except Exception as e:
            await self.safe_send(ctx, f"❌ Erreur : {e}")

    @commands.command()
    async def restoreconfig(self, ctx):
        if not await self.check_owner(ctx):
            return
        try:
            self.bot.db.restore()
            await self.safe_send(ctx, "💾 Configuration restaurée avec succès.")
        except Exception as e:
            await self.safe_send(ctx, f"❌ Erreur : {e}")

    # ---------------- Reset warns ----------------
    @commands.command()
    async def resetwarns(self, ctx, member_id: int):
        if not await self.check_owner(ctx):
            return
        self.bot.db.data.get("warns", {}).pop(str(member_id), None)
        self.bot.db.save()
        await self.safe_send(ctx, f"⚠️ Tous les warns de {member_id} ont été supprimés.")

    # ---------------- Check role / channel / member ----------------
    @commands.command()
    async def checkrole(self, ctx, role_id: int):
        if not await self.check_owner(ctx):
            return
        role = ctx.guild.get_role(role_id)
        if role:
            perms = [p[0] for p in role.permissions if p[1]]
            await self.safe_send(ctx, f"Rôle {role.name} : {perms}")
        else:
            await self.safe_send(ctx, "❌ Rôle introuvable.")

    @commands.command()
    async def checkchannel(self, ctx, channel_id: int):
        if not await self.check_owner(ctx):
            return
        channel = ctx.guild.get_channel(channel_id)
        if channel:
            await self.safe_send(ctx, f"Salon {channel.name} | Type={channel.type} | NSFW={getattr(channel, 'is_nsfw', False)}")
        else:
            await self.safe_send(ctx, "❌ Salon introuvable.")

    @commands.command()
    async def checkmember(self, ctx, member_id: int):
        if not await self.check_owner(ctx):
            return
        member = ctx.guild.get_member(member_id)
        if not member:
            return await self.safe_send(ctx, "❌ Membre introuvable.")
        roles = [r.name for r in member.roles if r.name != "@everyone"]
        await self.safe_send(ctx, f"Membre {member} | Rôles={roles} | Admin={member.guild_permissions.administrator}")

    # ---------------- List bots / servers / invite ----------------
    @commands.command()
    async def listbots(self, ctx):
        if not await self.check_owner(ctx):
            return
        bots = [m.name for m in ctx.guild.members if m.bot]
        await self.safe_send(ctx, f"Bots sur ce serveur : {', '.join(bots)}")

    @commands.command()
    async def servers(self, ctx, page: int = 1):
        if not await self.check_owner(ctx):
            return
        per_page = 5
        guilds = sorted(self.bot.guilds, key=lambda g: g.id, reverse=True)
        start = (page - 1) * per_page
        end = start + per_page
        msg = f"Serveurs (page {page}) :\n"
        for g in guilds[start:end]:
            msg += f"{g.name} | ID: {g.id} | Membres: {g.member_count}\n"
        await ctx.author.send(msg)

    @commands.command()
    async def invite(self, ctx, guild_id: int):
        if not await self.check_owner(ctx):
            return
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return await self.safe_send(ctx, "❌ Serveur introuvable.")
        channel = discord.utils.get(guild.text_channels, perms__create_instant_invite=True)
        if not channel:
            return await self.safe_send(ctx, "❌ Aucun salon disponible pour créer une invitation.")
        invite = await channel.create_invite(max_age=3600, max_uses=1)
        await ctx.author.send(f"Invitation pour {guild.name} : {invite}")

    # ---------------- Shutdown / Restart / PowerOn ----------------
    @commands.command()
    async def shutdownbot(self, ctx):
        if not await self.check_owner(ctx):
            return
        await self.safe_send(ctx, "⚠️ Arrêt du bot...")
        await self.bot.close()

    @commands.command()
    async def restartbot(self, ctx):
        if not await self.check_owner(ctx):
            return
        await self.safe_send(ctx, "⚠️ Redémarrage du bot...")
        await self.bot.close()

    @commands.command()
    async def poweron(self, ctx):
        if not await self.check_owner(ctx):
            return
        await self.safe_send(ctx, "✅ Services internes activés ou relancés.")

    # ---------------- Eval ----------------
    @commands.command()
    async def eval(self, ctx, *, code):
        if not await self.check_owner(ctx):
            return
        try:
            result = eval(code)
            if asyncio.iscoroutine(result):
                result = await result
            await self.safe_send(ctx, f"Résultat : {result}")
        except Exception:
            await self.safe_send(ctx, f"❌ Erreur :\n```{traceback.format_exc()}```")

    # ---------------- Set status ----------------
    @commands.command()
    async def setstatus(self, ctx, status: str, *, activity: str = None):
        if not await self.check_owner(ctx):
            return
        statuses = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "invisible": discord.Status.invisible
        }
        if status.lower() not in statuses:
            return await self.safe_send(ctx, f"❌ Statut invalide. Choix : {', '.join(statuses.keys())}")
        act = discord.Game(activity) if activity else None
        await self.bot.change_presence(status=statuses[status.lower()], activity=act)
        await self.safe_send(ctx, f"✅ Statut changé : {status.lower()} | Activité : {activity or 'Aucune'}")

# ---------------- Setup ----------------
async def setup(bot):
    if "creator" in bot.cogs:
        await bot.unload_extension("creator")
    await bot.add_cog(Creator(bot))
