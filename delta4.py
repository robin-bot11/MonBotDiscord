from discord.ext import commands
import discord
import asyncio
import traceback
import sys

OWNER_ID = 1383790178522370058

class Creator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------ Vérification OWNER ------------------
    def is_owner(self, ctx):
        return ctx.author.id == OWNER_ID

    # ------------------ PING ------------------
    @commands.command()
    async def ping(self, ctx):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé.")
        await ctx.send("Le bot est en ligne et répond correctement.")

    # ------------------ DM ------------------
    @commands.command()
    async def dm(self, ctx, user_id: int, *, message):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé.")
        user = await self.bot.fetch_user(user_id)
        try:
            await user.send(message)
            await ctx.send(f"Message envoyé à {user}.")
        except discord.Forbidden:
            await ctx.send("Impossible d'envoyer le message à cet utilisateur.")

    # ------------------ BACKUP / RESTORE ------------------
    @commands.command()
    async def backupconfig(self, ctx):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé.")
        try:
            self.bot.db.backup()
            await ctx.send("Configuration sauvegardée avec succès.")
        except Exception as e:
            await ctx.send(f"Erreur : {e}")

    @commands.command()
    async def restoreconfig(self, ctx):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé.")
        try:
            self.bot.db.restore()
            await ctx.send("Configuration restaurée avec succès.")
        except Exception as e:
            await ctx.send(f"Erreur : {e}")

    # ------------------ RESET WARNS ------------------
    @commands.command()
    async def resetwarns(self, ctx, member_id: int):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé.")
        self.bot.db.data["warns"].pop(str(member_id), None)
        self.bot.db.save()
        await ctx.send(f"Tous les warns de {member_id} ont été supprimés.")

    # ------------------ CHECK ROLE ------------------
    @commands.command()
    async def checkrole(self, ctx, role_id: int):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé.")
        role = ctx.guild.get_role(role_id)
        if role:
            perms = [p[0] for p in role.permissions if p[1]]
            await ctx.send(f"Rôle {role.name} : {perms}")
        else:
            await ctx.send("Rôle introuvable.")

    # ------------------ CHECK CHANNEL ------------------
    @commands.command()
    async def checkchannel(self, ctx, channel_id: int):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé.")
        channel = ctx.guild.get_channel(channel_id)
        if channel:
            await ctx.send(f"Salon {channel.name} : Type={channel.type}, NSFW={getattr(channel, 'is_nsfw', False)}")
        else:
            await ctx.send("Salon introuvable.")

    # ------------------ CHECK MEMBER ------------------
    @commands.command()
    async def checkmember(self, ctx, member_id: int):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé.")
        member = ctx.guild.get_member(member_id)
        if not member:
            return await ctx.send("Membre introuvable.")
        roles = [r.name for r in member.roles if r.name != "@everyone"]
        await ctx.send(f"Membre {member} : Rôles={roles}, Admin={member.guild_permissions.administrator}")

    # ------------------ LIST BOTS ------------------
    @commands.command()
    async def listbots(self, ctx):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé.")
        bots = [m.name for m in ctx.guild.members if m.bot]
        await ctx.send(f"Bots sur ce serveur : {', '.join(bots)}")

    # ------------------ SERVERS ------------------
    @commands.command()
    async def servers(self, ctx, page: int = 1):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé.")
        per_page = 5
        guilds = sorted(self.bot.guilds, key=lambda g: g.id, reverse=True)
        start = (page - 1) * per_page
        end = start + per_page
        msg = f"Serveurs (page {page}) :\n"
        for g in guilds[start:end]:
            msg += f"{g.name} | ID: {g.id} | Membres: {g.member_count}\n"
        await ctx.author.send(msg)

    # ------------------ INVITE ------------------
    @commands.command()
    async def invite(self, ctx, guild_id: int):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé.")
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return await ctx.send("Serveur introuvable.")
        channel = discord.utils.get(guild.text_channels, perms__create_instant_invite=True)
        if not channel:
            return await ctx.send("Aucun salon disponible pour créer une invitation.")
        invite = await channel.create_invite(max_age=3600, max_uses=1)
        await ctx.author.send(f"Invitation pour {guild.name} : {invite}")

    # ------------------ SHUTDOWN / RESTART / POWERON ------------------
    @commands.command()
    async def shutdownbot(self, ctx):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé.")
        await ctx.send("Arrêt du bot...")
        await self.bot.close()

    @commands.command()
    async def restartbot(self, ctx):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé.")
        await ctx.send("Redémarrage du bot...")
        await self.bot.close()

    @commands.command()
    async def poweron(self, ctx):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé.")
        await ctx.send("Services internes activés ou relancés.")

    # ------------------ EVAL ------------------
    @commands.command()
    async def eval(self, ctx, *, code):
        if not self.is_owner(ctx):
            return await ctx.send("Vous n'êtes pas autorisé.")
        try:
            result = eval(code)
            if asyncio.iscoroutine(result):
                result = await result
            await ctx.send(f"Résultat : {result}")
        except Exception:
            await ctx.send(f"Erreur :\n```{traceback.format_exc()}```")

# ------------------ Setup ------------------
async def setup(bot):
    await bot.add_cog(Creator(bot))
