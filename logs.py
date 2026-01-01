# logs.py
from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlog(self, ctx, log_type: str, channel: discord.TextChannel):
        """Configurer un salon pour un type de log"""
        valid_types = ["members", "channels", "messages", "voice", "mod", "role"]
        if log_type.lower() not in valid_types:
            return await ctx.send(f"❌ Type invalide. Types valides : {', '.join(valid_types)}")
        self.bot.db.set_log_channel(ctx.guild.id, log_type.lower(), channel.id)
        await ctx.send(f"✅ Logs de type `{log_type}` configurés dans {channel.mention}")

    async def send_log(self, guild, log_type, embed):
        """Envoyer un embed dans le salon configuré pour le type de log"""
        channel_id = self.bot.db.get_log_channel(guild.id, log_type.lower())
        if not channel_id:
            return
        channel = guild.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)

    # --- Membres ---
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        embed = discord.Embed(
            title="Nouveau membre",
            description=f"{member.mention} a rejoint le serveur.",
            color=COLOR
        )
        await self.send_log(member.guild, "members", embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return
        embed = discord.Embed(
            title="Départ d'un membre",
            description=f"{member} a quitté le serveur.",
            color=COLOR
        )
        await self.send_log(member.guild, "members", embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.bot:
            return
        changements = []

        # Pseudo
        if before.nick != after.nick:
            anciens = before.nick or before.name
            nouveaux = after.nick or after.name
            changements.append(f"Pseudo : {anciens} → {nouveaux}")

        # Rôles (exclut @everyone)
        before_roles = set(r for r in before.roles if r.name != "@everyone")
        after_roles = set(r for r in after.roles if r.name != "@everyone")
        ajoutes = after_roles - before_roles
        supprimes = before_roles - after_roles
        if ajoutes:
            changements.append("Rôles ajoutés : " + ", ".join(r.name for r in ajoutes))
        if supprimes:
            changements.append("Rôles retirés : " + ", ".join(r.name for r in supprimes))

        if changements:
            embed = discord.Embed(
                title=f"Membre mis à jour : {after}",
                description="\n".join(changements),
                color=COLOR
            )
            await self.send_log(after.guild, "members", embed)

    # --- Salons ---
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        embed = discord.Embed(
            title="Salon créé",
            description=f"{channel.name} a été créé.",
            color=COLOR
        )
        await self.send_log(channel.guild, "channels", embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        embed = discord.Embed(
            title="Salon supprimé",
            description=f"{channel.name} a été supprimé.",
            color=COLOR
        )
        await self.send_log(channel.guild, "channels", embed)

    # --- Messages ---
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        embed = discord.Embed(
            title="Message supprimé",
            description=(
                f"**Auteur :** {message.author}\n"
                f"**Salon :** {message.channel.mention}\n"
                f"**Message :** {message.content}"
            ),
            color=COLOR
        )
        await self.send_log(message.guild, "messages", embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        embed = discord.Embed(
            title="Message édité",
            description=(
                f"**Auteur :** {before.author}\n"
                f"**Salon :** {before.channel.mention}\n"
                f"**Avant :** {before.content}\n"
                f"**Après :** {after.content}"
            ),
            color=COLOR
        )
        await self.send_log(before.guild, "messages", embed)


# ---------------- Setup ----------------
async def setup(bot):
    await bot.add_cog(Logs(bot))
