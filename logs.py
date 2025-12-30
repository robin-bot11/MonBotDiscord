import discord
from discord.ext import commands

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = None  # ID du salon de logs à configurer

    # Commande pour configurer le salon de logs
    @commands.command(name="setlog")
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx, channel: discord.TextChannel):
        """Configure le salon de logs"""
        self.log_channel_id = channel.id
        await ctx.send(f"✅ Salon de logs configuré sur {channel.mention}")

    # Fonction utilitaire pour envoyer les logs
    async def send_log(self, embed: discord.Embed):
        if self.log_channel_id:
            channel = self.bot.get_channel(self.log_channel_id)
            if channel:
                await channel.send(embed=embed)

    # LOG Messages supprimés
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        embed = discord.Embed(
            title="Message supprimé",
            description=f"**Auteur:** {message.author}\n**Salon:** {message.channel}\n**Contenu:** {message.content}",
            color=0x6b00cb
        )
        await self.send_log(embed)

    # LOG Messages édités
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        embed = discord.Embed(
            title="Message édité",
            description=f"**Auteur:** {before.author}\n**Salon:** {before.channel}\n**Avant:** {before.content}\n**Après:** {after.content}",
            color=0x6b00cb
        )
        await self.send_log(embed)

    # LOG membres qui rejoignent
    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title="Nouveau membre",
            description=f"{member.mention} a rejoint le serveur.",
            color=0x6b00cb
        )
        await self.send_log(embed)

    # LOG membres qui quittent
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title="Membre parti",
            description=f"{member} a quitté le serveur.",
            color=0x6b00cb
        )
        await self.send_log(embed)

    # LOG rôles ajoutés ou retirés
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            added = [r.name for r in after.roles if r not in before.roles]
            removed = [r.name for r in before.roles if r not in after.roles]
            desc = ""
            if added:
                desc += f"**Rôles ajoutés:** {', '.join(added)}\n"
            if removed:
                desc += f"**Rôles retirés:** {', '.join(removed)}"
            if desc:
                embed = discord.Embed(
                    title=f"Mise à jour rôles de {after}",
                    description=desc,
                    color=0x6b00cb
                )
                await self.send_log(embed)

    # LOG changement de pseudo ou d'avatar
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        changes = []
        if before.nick != after.nick:
            changes.append(f"Pseudo : {before.nick} → {after.nick}")
        if before.avatar != after.avatar:
            changes.append(f"Avatar changé")
        if changes:
            embed = discord.Embed(
                title=f"Mise à jour profil de {after}",
                description="\n".join(changes),
                color=0x6b00cb
            )
            await self.send_log(embed)

    # LOG salons créés/supprimés
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        embed = discord.Embed(
            title="Salon créé",
            description=f"Nom : {channel.name}\nType : {channel.type}",
            color=0x6b00cb
        )
        await self.send_log(embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        embed = discord.Embed(
            title="Salon supprimé",
            description=f"Nom : {channel.name}\nType : {channel.type}",
            color=0x6b00cb
        )
        await self.send_log(embed)

    # LOG Voice State (entrer/quitter micro)
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        embed = None
        if before.channel != after.channel:
            if after.channel:
                embed = discord.Embed(
                    title="Membre rejoint un salon vocal",
                    description=f"{member} a rejoint {after.channel}",
                    color=0x6b00cb
                )
            elif before.channel:
                embed = discord.Embed(
                    title="Membre quitté un salon vocal",
                    description=f"{member} a quitté {before.channel}",
                    color=0x6b00cb
                )
        if embed:
            await self.send_log(embed)

def setup(bot):
    bot.add_cog(Logs(bot))
