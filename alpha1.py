import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import random
from base_donnees import Database  # renommer selon ton fichier

COLOR_DEFAULT = 0x6b00cb
MAX_TRIES = 3

EMOJIS = ["🩵", "💚", "🩷", "🧡", "💜"]

# ---------------- Sélection d'emoji ----------------
class VerificationSelect(Select):
    def __init__(self, correct_emoji, member, role_to_give, role_to_remove, db, guild_id):
        self.correct_emoji = correct_emoji
        self.member = member
        self.role_to_give = role_to_give
        self.role_to_remove = role_to_remove
        self.db = db
        self.guild_id = guild_id

        options = [discord.SelectOption(label=e) for e in EMOJIS]
        super().__init__(placeholder="Sélectionnez l'emoji correct", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        guild_data = self.db.data.get("verification", {}).get(str(self.guild_id), {})
        member_tries = guild_data.get("tries", {}).get(str(self.member.id), 0)

        if self.values[0] == self.correct_emoji:
            try:
                await self.member.add_roles(self.role_to_give, reason="Vérification réussie")
                if self.role_to_remove:
                    await self.member.remove_roles(self.role_to_remove, reason="Vérification réussie")
                await interaction.response.edit_message(content=f"✅ {self.member.mention}, vous êtes vérifié !", view=None)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Je n'ai pas les permissions pour gérer les rôles.", ephemeral=True)
        else:
            member_tries += 1
            guild_data.setdefault("tries", {})[str(self.member.id)] = member_tries
            self.db.data["verification"][str(self.guild_id)] = guild_data
            self.db.save()

            if member_tries >= MAX_TRIES:
                try:
                    await self.member.kick(reason="Échec de la vérification (3 essais)")
                    await interaction.response.edit_message(content=f"❌ {self.member.mention} a été expulsé après 3 essais.", view=None)
                except discord.Forbidden:
                    await interaction.response.send_message("❌ Impossible d'expulser ce membre.", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ Mauvais emoji, il vous reste {MAX_TRIES - member_tries} essais.", ephemeral=True)

# ---------------- Vue du bouton ----------------
class VerificationView(View):
    def __init__(self, correct_emoji, member, role_to_give, role_to_remove, db, guild_id, button_text):
        super().__init__(timeout=None)
        self.correct_emoji = correct_emoji
        self.member = member
        self.role_to_give = role_to_give
        self.role_to_remove = role_to_remove
        self.db = db
        self.guild_id = guild_id
        self.button_text = button_text
        self.add_item(Button(label=button_text, style=discord.ButtonStyle.green, custom_id="verify_button"))

    @discord.ui.button(label="Se vérifier", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify_button(self, button: Button, interaction: discord.Interaction):
        if interaction.user != self.member:
            return await interaction.response.send_message("❌ Ce bouton n'est pas pour vous.", ephemeral=True)
        view = View(timeout=None)
        view.add_item(VerificationSelect(
            self.correct_emoji, self.member, self.role_to_give, self.role_to_remove, self.db, self.guild_id
        ))
        await interaction.response.edit_message(content="Veuillez sélectionner l'emoji correct :", view=view)

# ---------------- Cog principal ----------------
class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setupverify(self, ctx):
        """Configuration interactive de la vérification"""
        guild_id = str(ctx.guild.id)
        self.db.data.setdefault("verification", {})
        self.db.data["verification"].setdefault(guild_id, {})

        # Titre
        await ctx.send("📌 Entrez le **titre** de l'embed de vérification :")
        msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        title = msg.content

        # Description
        await ctx.send("📌 Entrez la **description** de l'embed :")
        msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        description = msg.content

        # Texte du bouton
        await ctx.send("📌 Entrez le **texte du bouton** :")
        msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        button_text = msg.content

        # Rôle à donner après vérification
        await ctx.send("📌 Mentionnez le **rôle à donner** après vérification :")
        msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        role_to_give = ctx.guild.get_role(int(msg.content.strip("<@&>")))

        # Rôle d'isolation automatique
        guild_data = self.db.data["verification"][guild_id]
        isolation_role_id = guild_data.get("isolation_role")
        if not isolation_role_id:
            try:
                isolation_role = await ctx.guild.create_role(name="Non vérifié", reason="Rôle d'isolation")
                self.db.data["verification"][guild_id]["isolation_role"] = isolation_role.id
                # Restreindre tous les salons existants
                for channel in ctx.guild.text_channels:
                    await channel.set_permissions(isolation_role, read_messages=False)
            except discord.Forbidden:
                await ctx.send("❌ Je n'ai pas les permissions pour créer le rôle d'isolation.")
        else:
            isolation_role = ctx.guild.get_role(isolation_role_id)

        self.db.data["verification"][guild_id].update({
            "title": title,
            "description": description,
            "button_text": button_text,
            "role_to_give": role_to_give.id
        })
        self.db.save()

        # Envoi du message de vérification
        embed = discord.Embed(title=title, description=description, color=COLOR_DEFAULT)
        view = VerificationView(
            correct_emoji=random.choice(EMOJIS),
            member=None,
            role_to_give=role_to_give,
            role_to_remove=isolation_role,
            db=self.db,
            guild_id=ctx.guild.id,
            button_text=button_text
        )
        msg = await ctx.send(embed=embed, view=view)
        self.db.data["verification"][guild_id]["last_message"] = msg.id
        self.db.data["verification"][guild_id]["last_emoji"] = view.correct_emoji
        self.db.save()
        await ctx.send(f"✅ Configuration terminée et message de vérification envoyé dans {ctx.channel.mention}")

# ---------------- Setup ----------------
async def setup(bot):
    await bot.add_cog(Verification(bot))
