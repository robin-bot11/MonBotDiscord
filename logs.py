# journaux.py
from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels = {}  # {guild_id: {type: channel_id}}

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlog(self, ctx, log_type: str, channel: discord.TextChannel):
        """Configurer un salon pour un type de log"""
        guild_id = ctx.guild.id
        if guild_id not in self.channels:
            self.channels[guild_id] = {}
        self.channels[guild_id][log_type.lower()] = channel.id
        await ctx.send(embed=discord.Embed(
            description=f"Salon configuré pour {log_type} : {channel.mention}",
            color=COLOR
        ))

    async def send_log(self, guild, log_type, embed):
        """Envoyer un embed dans le salon configuré pour le type de log"""
        guild_id = guild.id
        if guild_id in self.channels and log_type in self.channels[guild_id]:
            channel_id = self.channels[guild_id][log_type]
            channel = guild.get_channel(channel_id)
            if channel:
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title="Nouveau membre",
            description=f"{member} a rejoint le serveur.",
            color=COLOR
        )
        await self.send_log(member.guild, "membres", embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title="Départ d'un membre",
            description=f"{member} a quitté le serveur.",
            color=COLOR
        )
        await self.send_log(member.guild, "membres", embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        changes = []
        if before.nick != after.nick:
            changes.append(f"Pseudo : {before.nick} → {after.nick}")
        before_roles = set(before.roles)
        after_roles = set(after.roles)
        added_roles = after_roles - before_roles
        removed_roles = before_roles - after_roles
        if added_roles:
            changes.append("Rôles ajoutés : " + ", ".join(r.name for r in added_roles))
        if removed_roles:
            changes.append("Rôles retirés : " + ", ".join(r.name for r in removed_roles))
        if changes:
            embed = discord.Embed(
                title=f"Membre mis à jour : {after}",
                description="\n".join(changes),
                color=COLOR
            )
            await self.send_log(after.guild, "membres", embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        embed = discord.Embed(
            title="Salon créé",
            description=f"{channel.name} a été créé.",
            color=COLOR
        )
        await self.send_log(channel.guild, "salon", embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        embed = discord.Embed(
            title="Salon supprimé",
            description=f"{channel.name} a été supprimé.",
            color=COLOR
        )
        await self.send_log(channel.guild, "salon", embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        embed = discord.Embed(
            title="Message supprimé",
            description=f"**Auteur :** {message.author}\n**Salon :** {message.channel.mention}\n**Message :** {message.content}",
            color=COLOR
        )
        await self.send_log(message.guild, "messages", embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        embed = discord.Embed(
            title="Message édité",
            description=f"**Auteur :** {before.author}\n**Salon :** {before.channel.mention}\n**Avant :** {before.content}\n**Après :** {after.content}",
            color=COLOR
        )
        await self.send_log(before.guild, "messages", embed)

def setup(bot):
    bot.add_cog(Logs(bot))
