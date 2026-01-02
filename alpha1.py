import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import random
from storx import Database  # base de données renommée

COLOR_DEFAULT = 0x6b00cb
MAX_TRIES = 3
EMOJIS = ["🩵", "💚", "🩷", "🧡", "💜"]


# ---------------- Sélecteur d’emoji ----------------
class VerificationSelect(Select):
    def __init__(self, correct_emoji, member, role_valid, role_isolation, db, guild_id):
        self.correct_emoji = correct_emoji
        self.member = member
        self.role_valid = role_valid
        self.role_isolation = role_isolation
        self.db = db
        self.guild_id = guild_id

        options = [discord.SelectOption(label=e) for e in EMOJIS]

        super().__init__(
            placeholder="Sélectionnez l’emoji correct",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.member.id:
            return await interaction.response.send_message(
                "Cette interaction ne vous est pas destinée.",
                ephemeral=True
            )

        data = self.db.data.setdefault("verification", {}).setdefault(str(self.guild_id), {})
        tries = data.setdefault("tries", {}).get(str(self.member.id), 0)

        # ✅ BON EMOJI
        if self.values[0] == self.correct_emoji:
            try:
                await self.member.add_roles(self.role_valid, reason="Vérification réussie")
                if self.role_isolation:
                    await self.member.remove_roles(self.role_isolation, reason="Vérification réussie")

                await interaction.response.edit_message(
                    content="Vérification réussie. Accès débloqué.",
                    view=None
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "Permissions insuffisantes pour gérer les rôles.",
                    ephemeral=True
                )
            return

        # ❌ MAUVAIS EMOJI
        tries += 1
        data["tries"][str(self.member.id)] = tries
        self.db.save()

        if tries >= MAX_TRIES:
            try:
                await self.member.kick(reason="Échec de la vérification (3 tentatives)")
            except discord.Forbidden:
                pass

            await interaction.response.edit_message(
                content="Échec de la vérification. Vous avez été expulsé.",
                view=None
            )
        else:
            await interaction.response.send_message(
                f"Mauvais choix. Tentatives restantes : {MAX_TRIES - tries}.",
                ephemeral=True
            )


# ---------------- Vue bouton ----------------
class VerificationView(View):
    def __init__(self, correct_emoji, member, role_valid, role_isolation, db, guild_id, button_text):
        super().__init__(timeout=None)
        self.correct_emoji = correct_emoji
        self.member = member
        self.role_valid = role_valid
        self.role_isolation = role_isolation
        self.db = db
        self.guild_id = guild_id

        self.add_item(
            Button(
                label=button_text,
                style=discord.ButtonStyle.green,
                custom_id=f"verify_{guild_id}"
            )
        )

    @discord.ui.button(label="Vérification", style=discord.ButtonStyle.green)
    async def verify_button(self, button: Button, interaction: discord.Interaction):
        if interaction.user.id != self.member.id:
            return await interaction.response.send_message(
                "Ce bouton ne vous est pas destiné.",
                ephemeral=True
            )

        view = View(timeout=None)
        view.add_item(
            VerificationSelect(
                self.correct_emoji,
                self.member,
                self.role_valid,
                self.role_isolation,
                self.db,
                self.guild_id
            )
        )

        await interaction.response.edit_message(
            content="Sélectionnez l’emoji correct.",
            view=view
        )


# ---------------- Cog principal ----------------
class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setupverify(self, ctx):
        guild_id = str(ctx.guild.id)
        self.db.data.setdefault("verification", {})
        self.db.data["verification"].setdefault(guild_id, {})

        # Titre
        await ctx.send("Entrez le titre de l’embed de vérification :")
        title = (await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)).content

        # Description
        await ctx.send("Entrez la description de l’embed :")
        description = (await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)).content

        # Texte bouton
        await ctx.send("Entrez le texte du bouton :")
        button_text = (await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)).content

        # Rôle validé
        await ctx.send("Mentionnez le rôle à donner après vérification :")
        role_msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
        role_valid = ctx.guild.get_role(int(role_msg.content.strip("<@&>")))

        # Rôle isolation (obligatoire)
        data = self.db.data["verification"][guild_id]
        role_isolation = None

        if "isolation_role" not in data:
            role_isolation = await ctx.guild.create_role(
                name="Non vérifié",
                reason="Rôle automatique de vérification"
            )
            data["isolation_role"] = role_isolation.id

            for channel in ctx.guild.channels:
                try:
                    await channel.set_permissions(role_isolation, read_messages=False)
                except:
                    pass
        else:
            role_isolation = ctx.guild.get_role(data["isolation_role"])

        # Sauvegarde config
        data.update({
            "title": title,
            "description": description,
            "button_text": button_text,
            "role_valid": role_valid.id
        })
        self.db.save()

        # Envoi message
        embed = discord.Embed(
            title=title,
            description=description,
            color=COLOR_DEFAULT
        )

        emoji = random.choice(EMOJIS)

        view = VerificationView(
            correct_emoji=emoji,
            member=None,
            role_valid=role_valid,
            role_isolation=role_isolation,
            db=self.db,
            guild_id=ctx.guild.id,
            button_text=button_text
        )

        msg = await ctx.send(embed=embed, view=view)

        data["message_id"] = msg.id
        data["emoji"] = emoji
        self.db.save()

        await ctx.send("Système de vérification configuré avec succès.")


# ---------------- Setup ----------------
async def setup(bot):
    await bot.add_cog(Verification(bot))
