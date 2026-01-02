import discord
from discord.ext import commands
from storx import Database

COLOR_DEFAULT = 0x6b00cb


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    # ---------------- MEMBER JOIN ----------------
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_id = str(member.guild.id)
        data = self.db.data.get("verification", {}).get(guild_id)

        if not data:
            return

        # Role d'isolation
        isolation_role_id = data.get("isolation_role")
        if isolation_role_id:
            role = member.guild.get_role(isolation_role_id)
            if role:
                try:
                    await member.add_roles(role, reason="Automatic isolation")
                except discord.Forbidden:
                    pass

        channel_id = data.get("welcome_channel")
        if not channel_id:
            return

        channel = member.guild.get_channel(channel_id)
        if not channel:
            return

        # Variables
        def parse(text):
            return (
                text.replace("{user}", member.mention)
                .replace("{server}", member.guild.name)
                .replace("{members}", str(member.guild.member_count))
            )

        # EMBED
        if data.get("welcome_type") == "embed":
            embed = discord.Embed(
                title=parse(data.get("welcome_title", "")),
                description=parse(data.get("welcome_description", "")),
                color=COLOR_DEFAULT
            )
            await channel.send(embed=embed)

        # MESSAGE SIMPLE
        elif data.get("welcome_type") == "text":
            message = data.get("welcome_message")
            if message:
                await channel.send(parse(message))

    # ---------------- SET WELCOME TEXT ----------------
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcome(self, ctx, channel: discord.TextChannel, *, message: str):
        guild_id = str(ctx.guild.id)

        self.db.data.setdefault("verification", {})
        self.db.data["verification"].setdefault(guild_id, {})

        self.db.data["verification"][guild_id].update({
            "welcome_type": "text",
            "welcome_channel": channel.id,
            "welcome_message": message
        })
        self.db.save()

        embed = discord.Embed(
            title="Welcome activé (message)",
            description=f"Salon : {channel.mention}\n\n{message}",
            color=COLOR_DEFAULT
        )
        await ctx.send(embed=embed)

    # ---------------- SET WELCOME EMBED ----------------
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcomeembed(self, ctx, channel: discord.TextChannel, *, content: str):
        if "|" not in content:
            return await ctx.send(
                "❌ Format invalide\nExemple : `+setwelcomeembed #salon Titre | Description`"
            )

        title, description = map(str.strip, content.split("|", 1))
        guild_id = str(ctx.guild.id)

        self.db.data.setdefault("verification", {})
        self.db.data["verification"].setdefault(guild_id, {})

        self.db.data["verification"][guild_id].update({
            "welcome_type": "embed",
            "welcome_channel": channel.id,
            "welcome_title": title,
            "welcome_description": description
        })
        self.db.save()

        embed = discord.Embed(
            title="Welcome activé (embed)",
            description=f"Salon : {channel.mention}",
            color=COLOR_DEFAULT
        )
        embed.add_field(name="Titre", value=title, inline=False)
        embed.add_field(name="Description", value=description, inline=False)

        await ctx.send(embed=embed)

    # ---------------- DELWELCOME ----------------
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def delwelcome(self, ctx):
        guild_id = str(ctx.guild.id)
        data = self.db.data.get("verification", {}).get(guild_id)

        if not data:
            return await ctx.send("❌ Aucun welcome configuré.")

        keys = [
            "welcome_type",
            "welcome_channel",
            "welcome_message",
            "welcome_title",
            "welcome_description"
        ]

        for key in keys:
            data.pop(key, None)

        self.db.save()

        embed = discord.Embed(
            title="Welcome désactivé",
            description="Le système de bienvenue est maintenant OFF.",
            color=COLOR_DEFAULT
        )
        await ctx.send(embed=embed)


# ---------------- Setup ----------------
async def setup(bot):
    await bot.add_cog(Welcome(bot))
