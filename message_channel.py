# message_channel.py
from discord.ext import commands
import discord

COLOR = 0x6b00cb

class MessageChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------ SAY ------------------
    @commands.command(name="say")
    @commands.has_permissions(administrator=True)
    async def say(self, ctx, *, message: str):
        """Envoyer un message simple"""
        await ctx.send(message)

    @say.error
    async def say_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

    # ------------------ SAYEMBED ------------------
    @commands.command(name="sayembed")
    @commands.has_permissions(administrator=True)
    async def sayembed(self, ctx, *, message: str):
        """Envoyer un message en embed"""
        embed = discord.Embed(description=message, color=COLOR)
        await ctx.send(embed=embed)

    @sayembed.error
    async def sayembed_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

    # ------------------ CREATE CHANNEL ------------------
    @commands.command(name="createchannel")
    @commands.has_permissions(manage_channels=True)
    async def createchannel(self, ctx, name: str, type_: str = "text"):
        """Créer un salon textuel ou vocal"""
        type_lower = type_.lower()
        if type_lower == "voice":
            await ctx.guild.create_voice_channel(name)
            await ctx.send(f"✅ Salon vocal '{name}' créé.")
        else:
            await ctx.guild.create_text_channel(name)
            await ctx.send(f"✅ Salon textuel '{name}' créé.")

    @createchannel.error
    async def createchannel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Vous n'avez pas la permission de créer des salons.")
        else:
            await ctx.send(f"❌ Erreur : {error}")

    # ------------------ DELETE CHANNEL ------------------
    @commands.command(name="deletechannel")
    @commands.has_permissions(manage_channels=True)
    async def deletechannel(self, ctx, channel: discord.abc.GuildChannel):
        """Supprimer un salon textuel ou vocal"""
        await channel.delete()
        await ctx.send(f"✅ Salon '{channel.name}' supprimé.")

    @deletechannel.error
    async def deletechannel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Vous n'avez pas la permission de supprimer des salons.")
        else:
            await ctx.send(f"❌ Erreur : {error}")

# ------------------ Setup ------------------
async def setup(bot):
    await bot.add_cog(MessageChannel(bot))
