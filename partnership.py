from discord.ext import commands
import discord
import re

COLOR = 0x6b00cb
OWNER_ID = 1383790178522370058
INVITE_REGEX = r"(https?:\/\/)?(www\.)?(discord\.gg|discord\.com\/invite)\/\S+"

class Partenariat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner(self, ctx):
        return ctx.author.id == OWNER_ID

    # ───────── CONFIG SALON ─────────
    @commands.command()
    async def setpartnerchannel(self, ctx, channel: discord.TextChannel):
        if not self.is_owner(ctx):
            return await ctx.send("❌ Commande réservée à l’owner.")

        self.bot.db.set_partner_channel(ctx.guild.id, channel.id)
        await ctx.send(f"✅ Salon partenariat défini sur {channel.mention}")

    # ───────── CONFIG ROLE ─────────
    @commands.command()
    async def setpartnerrole(self, ctx, role: discord.Role):
        if not self.is_owner(ctx):
            return await ctx.send("❌ Commande réservée à l’owner.")

        self.bot.db.set_partner_role(ctx.guild.id, role.id)
        await ctx.send(f"✅ Rôle partenariat défini : {role.mention}")

    # ───────── DÉTECTION LIEN ─────────
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        guild_id = message.guild.id
        channel_id = self.bot.db.get_partner_channel(guild_id)
        role_id = self.bot.db.get_partner_role(guild_id)

        if not channel_id or not role_id:
            return

        if message.channel.id != channel_id:
            return

        if re.search(INVITE_REGEX, message.content):
            role = message.guild.get_role(role_id)
            if role:
                await message.channel.send(f"🤝 Nouveau partenariat ! {role.mention}")

async def setup(bot):
    await bot.add_cog(Partenariat(bot))
