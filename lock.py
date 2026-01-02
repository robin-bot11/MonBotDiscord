# logs.py
from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # Accès à self.bot.db

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlog(self, ctx, log_type: str, channel: discord.TextChannel):
        """
        Configurer le salon de logs.
        log_type : role, mod, voice, channel, message, member
        """
        guild_id = str(ctx.guild.id)
        log_type = log_type.lower()
        valid_types = ["role", "mod", "voice", "channel", "message", "member"]
        if log_type not in valid_types:
            return await ctx.send(f"❌ Type de log invalide. Types valides : {', '.join(valid_types)}")

        self.bot.db.set_log_channel(guild_id, log_type, channel.id)
        await ctx.send(f"✅ Salon de logs pour `{log_type}` défini : {channel.mention}")

    async def send_log(self, guild, log_type, embed):
        """Envoi un embed dans le salon de logs configuré"""
        channel_id = self.bot.db.get_log_channel(guild.id, log_type.lower())
        if not channel_id:
            return
        channel = guild.get_channel(channel_id)
        if not channel:
            return
        await channel.send(embed=embed)

    # Exemple : log d'édition de message
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content == after.content:
            return
        embed = discord.Embed(
            title="✏️ Message édité",
            description=f"Avant : {before.content}\nAprès : {after.content}",
            color=COLOR
        )
        embed.set_author(name=before.author, icon_url=before.author.display_avatar.url)
        embed.add_field(name="Salon", value=before.channel.mention)
        await self.send_log(before.guild, "message", embed)

    # Exemple : log de suppression de message
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        embed = discord.Embed(
            title="🗑️ Message supprimé",
            description=message.content,
            color=COLOR
        )
        embed.set_author(name=message.author, icon_url=message.author.display_avatar.url)
        embed.add_field(name="Salon", value=message.channel.mention)
        await self.send_log(message.guild, "message", embed)

# ✅ Correct pour Discord.py 2.x
async def setup(bot):
    await bot.add_cog(Logs(bot))
