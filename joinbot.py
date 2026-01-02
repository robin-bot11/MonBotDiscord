import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import random
from storx import Database  # Ta base de données renommée

COLOR_DEFAULT = 0x6b00cb
MAX_TRIES = 3
EMOJIS = ["🩵", "💚", "🩷", "🧡", "💜"]

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

        data = self.db.data.setdefault("verification", {}).setdefault(str(self.guild_id), {})
        tries = data.setdefault("tries", {}).get(str(self.member.id), 0)

        if self.values[0] == self.correct_emoji:
            try:
                await self.member.add_roles(self.role_valid, reason="Vérification réussie")
                if self.role_isolation:
                    await self.member.remove_roles(self.role_isolation, reason="Vérification réussie")
                await interaction.response.edit_message(content="✅ Vérification réussie !", view=None)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Permissions insuffisantes.", ephemeral=True)
            return

        tries += 1
        data["tries"][str(self.member.id)] = tries
        self.db.save()

        if tries >= MAX_TRIES:
            try:
                await self.member.kick(reason="Échec de la vérification (3 tentatives)")
            except discord.Forbidden:
                pass
            await interaction.response.edit_message(content="❌ Échec. Vous avez été expulsé.", view=None)
        else:
            await interaction.response.send_message(f"❌ Mauvais choix. Tentatives restantes : {MAX_TRIES - tries}.", ephemeral=True)


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
        view.add_item(VerificationSelect(self.correct_emoji, self.member, self.role_valid, self.role_isolation, self.db, self.guild_id))
        await interaction.response.edit_message(content="Sélectionnez l'emoji correct :", view=view)


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
        self.db.data.setdefault("verification", {})
        self.db.data["verification"].setdefault(guild_id, {})

        await ctx.send("📌 Entrez le titre de l'embed de vérification :")
        title = (await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)).content

        await ctx.send("📌 Entrez la description de l'embed :")
        description = (await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)).content

        await ctx.send("📌 Entrez le texte du bouton :")
        button_text = (await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)).content

        await ctx.send("📌 Mentionnez le rôle à donner après vérification :")
        role_msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
        role_valid = ctx.guild.get_role(int(role_msg.content.strip("<@&>")))

        data = self.db.data["verification"][guild_id]
        role_isolation = None
        if "isolation_role" not in data:
            role_isolation = await ctx.guild.create_role(name="Non vérifié", reason="Rôle automatique")
            data["isolation_role"] = role_isolation.id
            for channel in ctx.guild.channels:
                try:
                    await channel.set_permissions(role_isolation, read_messages=False)
                except:
                    pass
        else:
            role_isolation = ctx.guild.get_role(data["isolation_role"])

        data.update({"title": title, "description": description, "button_text": button_text, "role_valid": role_valid.id})
        self.db.save()

        embed = discord.Embed(title=title, description=description, color=COLOR_DEFAULT)
        emoji = random.choice(EMOJIS)
        view = VerificationView(correct_emoji=emoji, member=None, role_valid=role_valid, role_isolation=role_isolation, db=self.db, guild_id=ctx.guild.id, button_text=button_text)
        msg = await ctx.send(embed=embed, view=view)
        data["message_id"] = msg.id
        data["emoji"] = emoji
        self.db.save()
        await ctx.send("✅ Système de vérification configuré.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcome(self, ctx, channel: discord.TextChannel, *, message):
        """Configurer le welcome simple (texte)"""
        guild_id = str(ctx.guild.id)
        self.db.data.setdefault("welcome", {})
        self.db.data["welcome"][guild_id] = {"channel": channel.id, "type": "text", "message": message, "enabled": True}
        self.db.save()
        await ctx.send(f"✅ Welcome configuré dans {channel.mention}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcomeembed(self, ctx, channel: discord.TextChannel, title, description, thumbnail_url=None, image_url=None):
        """Configurer le welcome en embed"""
        guild_id = str(ctx.guild.id)
        self.db.data.setdefault("welcome", {})
        self.db.data["welcome"][guild_id] = {
            "channel": channel.id,
            "type": "embed",
            "title": title,
            "description": description,
            "thumbnail": thumbnail_url,
            "image": image_url,
            "enabled": True
        }
        self.db.save()
        await ctx.send(f"✅ Embed de bienvenue configuré dans {channel.mention}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def togglewelcome(self, ctx):
        """Activer / désactiver le welcome sans supprimer la config"""
        guild_id = str(ctx.guild.id)
        welcome_data = self.db.data.get("welcome", {}).get(guild_id)
        if not welcome_data:
            return await ctx.send("⚠️ Aucun welcome configuré")
        welcome_data["enabled"] = not welcome_data.get("enabled", True)
        self.db.data["welcome"][guild_id] = welcome_data
        self.db.save()
        state = "activé" if welcome_data["enabled"] else "désactivé"
        await ctx.send(f"✅ Welcome {state}")

    # ----------------- Listener -----------------
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        data = self.db.data.get("verification", {}).get(guild_id, {})
        welcome_data = self.db.data.get("welcome", {}).get(guild_id)

        # Rôle d’isolation automatique
        isolation_role_id = data.get("isolation_role")
        if isolation_role_id:
            role = member.guild.get_role(isolation_role_id)
            if role:
                try:
                    await member.add_roles(role, reason="Rôle d'isolation automatique")
                except discord.Forbidden:
                    pass

        # Envoi welcome si activé
        if welcome_data and welcome_data.get("enabled", True):
            channel = member.guild.get_channel(welcome_data["channel"])
            if channel:
                if welcome_data["type"] == "text":
                    await channel.send(welcome_data["message"].replace("{user}", member.mention))
                else:
                    embed = discord.Embed(title=welcome_data.get("title", "Bienvenue !"), description=welcome_data.get("description", "").replace("{user}", member.mention), color=COLOR_DEFAULT)
                    if welcome_data.get("thumbnail"):
                        embed.set_thumbnail(url=welcome_data["thumbnail"])
                    if welcome_data.get("image"):
                        embed.set_image(url=welcome_data["image"])
                    await channel.send(embed=embed)

# ----------------- Setup -----------------
async def setup(bot):
    await bot.add_cog(WelcomeVerification(bot))
