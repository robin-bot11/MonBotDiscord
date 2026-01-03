import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import random
from storx import Database

COLOR_DEFAULT = 0x6b00cb
MAX_TRIES = 3
EMOJIS = ["🩵", "💚", "🩷", "🧡", "💜"]

# -------------------- Sélection d'emoji --------------------
class VerificationSelect(Select):
    def __init__(self, correct_emoji, member, role_valid, role_isolation, db, guild_id):
        self.correct_emoji = correct_emoji
        self.member = member
        self.role_valid = role_valid
        self.role_isolation = role_isolation
        self.db = db
        self.guild_id = guild_id
        options = [discord.SelectOption(label=e) for e in EMOJIS]
        super().__init__(placeholder="Sélectionnez l'emoji correct", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.member.id:
            return await interaction.response.send_message("❌ Ce bouton n'est pas pour vous.", ephemeral=True)

        tries = self.db.add_try(self.guild_id, self.member.id)

        if self.values[0] == self.correct_emoji:
            try:
                await self.member.add_roles(self.role_valid, reason="Vérification réussie")
                if self.role_isolation:
                    await self.member.remove_roles(self.role_isolation, reason="Vérification réussie")
                await interaction.response.edit_message(content="✅ Vérification réussie !", view=None)
                self.db.reset_tries(self.guild_id, self.member.id)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Permissions insuffisantes.", ephemeral=True)
            return

        if tries >= MAX_TRIES:
            try:
                await self.member.kick(reason="Échec de la vérification (3 tentatives)")
            except discord.Forbidden:
                pass
            await interaction.response.edit_message(content="❌ Échec. Vous avez été expulsé.", view=None)
        else:
            await interaction.response.send_message(
                f"❌ Mauvais choix. Tentatives restantes : {MAX_TRIES - tries}.", ephemeral=True
            )

# -------------------- Vue du bouton --------------------
class VerificationView(View):
    def __init__(self, correct_emoji, member, role_valid, role_isolation, db, guild_id, button_text):
        super().__init__(timeout=None)
        self.correct_emoji = correct_emoji
        self.member = member
        self.role_valid = role_valid
        self.role_isolation = role_isolation
        self.db = db
        self.guild_id = guild_id
        self.add_item(Button(label=button_text, style=discord.ButtonStyle.green, custom_id=f"verify_{guild_id}"))

    @discord.ui.button(label="Vérification", style=discord.ButtonStyle.green)
    async def verify_button(self, button: Button, interaction: discord.Interaction):
        if interaction.user.id != self.member.id:
            return await interaction.response.send_message("❌ Ce bouton n'est pas pour vous.", ephemeral=True)
        view = View(timeout=None)
        view.add_item(VerificationSelect(
            self.correct_emoji, self.member, self.role_valid, self.role_isolation, self.db, self.guild_id
        ))
        await interaction.response.edit_message(content="Sélectionnez l'emoji correct :", view=view)

# -------------------- Cog Welcome + Vérification --------------------
class WelcomeVerification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    # ----------------- Commandes Admin -----------------
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setupverify(self, ctx):
        """Configurer la vérification avec emoji"""
        guild_id = str(ctx.guild.id)

        await ctx.send("📌 Entrez le titre de l'embed de vérification :")
        title = (await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)).content

        await ctx.send("📌 Entrez la description de l'embed :")
        description = (await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)).content

        await ctx.send("📌 Entrez le texte du bouton :")
        button_text = (await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)).content

        await ctx.send("📌 Mentionnez le rôle à donner après vérification :")
        role_msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
        role_valid = ctx.guild.get_role(int(role_msg.content.strip("<@&>")))

        # Gestion rôle isolation
        data = self.db.get_verification(guild_id)
        if "isolation_role" not in data or data["isolation_role"] is None:
            role_isolation = await ctx.guild.create_role(name="Non vérifié", reason="Rôle automatique")
            for channel in ctx.guild.channels:
                try:
                    await channel.set_permissions(role_isolation, read_messages=False)
                except:
                    pass
        else:
            role_isolation = ctx.guild.get_role(data["isolation_role"])

        # Enregistrement DB
        emoji = random.choice(EMOJIS)
        msg = await ctx.send(
            embed=discord.Embed(title=title, description=description, color=COLOR_DEFAULT),
            view=VerificationView(emoji, None, role_valid, role_isolation, self.db, ctx.guild.id, button_text)
        )
        self.db.set_verification(
            guild_id,
            role_valid=role_valid.id,
            isolation_role=role_isolation.id if role_isolation else None,
            title=title,
            description=description,
            button_text=button_text,
            message_id=msg.id,
            emoji=emoji
        )

        await ctx.send("✅ Système de vérification configuré.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcome(self, ctx, channel: discord.TextChannel, *, message):
        """Configurer le welcome simple (texte)"""
        self.db.set_welcome(str(ctx.guild.id), channel_id=channel.id, message=message, embed_data=None, enabled=True)
        await ctx.send(f"✅ Welcome configuré dans {channel.mention}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcomeembed(self, ctx, channel: discord.TextChannel, title, description, thumbnail_url=None, image_url=None):
        """Configurer le welcome en embed"""
        embed_data = {"title": title, "description": description, "thumbnail": thumbnail_url, "image": image_url}
        self.db.set_welcome(str(ctx.guild.id), channel_id=channel.id, message=None, embed_data=embed_data, enabled=True)
        await ctx.send(f"✅ Embed de bienvenue configuré dans {channel.mention}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def togglewelcome(self, ctx):
        """Activer / désactiver le welcome sans supprimer la config"""
        state = self.db.toggle_welcome(str(ctx.guild.id))
        if state is None:
            await ctx.send("⚠️ Aucun welcome configuré")
        else:
            await ctx.send(f"✅ Welcome {'activé' if state else 'désactivé'}")

    # ----------------- Listener -----------------
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)

        # Vérification isolation
        data = self.db.get_verification(guild_id)
        isolation_role_id = data.get("isolation_role")
        if isolation_role_id:
            role = member.guild.get_role(isolation_role_id)
            if role:
                try:
                    await member.add_roles(role, reason="Rôle d'isolation automatique")
                except discord.Forbidden:
                    pass

        # Welcome
        welcome_data = self.db.get_welcome(guild_id)
        if welcome_data.get("enabled", True):
            channel = member.guild.get_channel(welcome_data.get("channel"))
            if channel:
                if welcome_data.get("embed_data"):
                    embed_info = welcome_data["embed_data"]
                    embed = discord.Embed(
                        title=embed_info.get("title", "Bienvenue !"),
                        description=embed_info.get("description", "").replace("{user}", member.mention),
                        color=COLOR_DEFAULT
                    )
                    if embed_info.get("thumbnail"):
                        embed.set_thumbnail(url=embed_info["thumbnail"])
                    if embed_info.get("image"):
                        embed.set_image(url=embed_info["image"])
                    await channel.send(embed=embed)
                else:
                    await channel.send(welcome_data.get("message", "").replace("{user}", member.mention))

# ----------------- Setup -----------------
async def setup(bot):
    await bot.add_cog(WelcomeVerification(bot))
