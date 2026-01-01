from discord.ext import commands
import discord

COLOR = 0x6b00cb
OWNER_ID = 1383790178522370058

class Partenariat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner(self, ctx):
        return ctx.author.id == OWNER_ID

    @commands.command(name="setpartnerrole")
    async def set_partner_role(self, ctx, role: discord.Role):
        """Configure le rôle à ping lorsqu’un lien d’invitation est posté"""
        if not self.is_owner(ctx):
            return await ctx.send("⛔ Vous n'êtes pas autorisé à utiliser cette commande.")
        
        self.bot.db.set_partner_role(ctx.guild.id, role.id)
        await ctx.send(f"✅ Partner role set: {role.mention}")

    @commands.command(name="setpartnerchannel")
    async def set_partner_channel(self, ctx, channel: discord.TextChannel):
        """Configure le channel où seront détectés les liens d’invitation"""
        if not self.is_owner(ctx):
            return await ctx.send("⛔ Vous n'êtes pas autorisé à utiliser cette commande.")
        
        self.bot.db.set_partner_channel(ctx.guild.id, channel.id)
        await ctx.send(f"✅ Partner channel set: {channel.mention}")

async def setup(bot):
    await bot.add_cog(Partenariat(bot))
