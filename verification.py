import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import random
from database import Database

COLOR_DEFAULT = 0x6b00cb
EMOJIS = ["🩵","💚","🩷","🧡","💜"]

class VerificationSelect(Select):
    def __init__(self, correct_emoji, member, role_to_give, role_to_remove, db, guild_id):
        options = [discord.SelectOption(label=e) for e in EMOJIS]
        super().__init__(placeholder="Sélectionnez l'emoji indiqué", min_values=1, max_values=1, options=options)
        self.correct_emoji = correct_emoji
        self.member = member
        self.role_to_give = role_to_give
        self.role_to_remove = role_to_remove
        self.db = db
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == self.correct_emoji:
            # Vérification réussie
            await self.member.add_roles(self.role_to_give, reason="Vérification réussie")
            if self.role_to_remove:
                await self.member.remove_roles(self.role_to_remove, reason="Vérification réussie")
            await interaction.response.edit_message(content=f"✅ {self.member.mention}, vous êtes vérifié !", view=None)
        else:
            await interaction.response.send_message("❌ Mauvais emoji, réessayez.", ephemeral=True)

class VerificationView(View):
    def __init__(self, correct_emoji, member, role_to_give, role_to_remove, db, guild_id, button_text):
        super().__init__(timeout=None)
        self.add_item(Button(label=button_text, style=discord.ButtonStyle.green, custom_id="verify_button"))
        self.correct_emoji = correct_emoji
        self.member = member
        self.role_to_give = role_to_give
        self.role_to_remove = role_to_remove
        self.db = db
        self.guild_id = guild_id

    @discord.ui.button(label="Se vérifier", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify_button(self, button: Button, interaction: discord.Interaction):
        # Affiche le select avec les emojis
        view = View(timeout=None)
        view.add_item(VerificationSelect(
            self.correct_emoji, self.member, self.role_to_give, self.role_to_remove, self.db, self.guild_id
        ))
        await interaction.response.edit_message(content="Veuillez sélectionner l'emoji correct ci-dessous :", view=view)

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    # ---------------- Commandes ----------------
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setverifyrole(self, ctx, role: discord.Role):
        """Définit le rôle à donner après vérification"""
        self.db.data.setdefault("verification", {})
        self.db.data["verification"].setdefault(str(ctx.guild.id), {})
        self.db.data["verification"][str(ctx.guild.id)]["role_to_give"] = role.id
        self.db.save()
        await ctx.send(f"Rôle à donner après vérification : {role.name}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setunverifiedrole(self, ctx, role: discord.Role = None):
        """Définit le rôle à retirer après vérification (optionnel)"""
        self.db.data.setdefault("verification", {})
        self.db.data["verification"].setdefault(str(ctx.guild.id), {})
        self.db.data["verification"][str(ctx.guild.id)]["role_to_remove"] = role.id if role else None
        self.db.save()
        msg = f"Rôle à retirer après vérification : {role.name}" if role else "Aucun rôle à retirer configuré"
        await ctx.send(msg)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sendverify(self, ctx, channel: discord.TextChannel, titre: str, *, description):
        """Envoie l'embed de vérification dans le salon configuré"""
        guild_data = self.db.data.get("verification", {}).get(str(ctx.guild.id), {})
        role_id = guild_data.get("role_to_give")
        role_to_remove_id = guild_data.get("role_to_remove")
        if not role_id:
            return await ctx.send("❌ Veuillez configurer le rôle à donner avec `+setverifyrole` avant.")

        role_to_give = ctx.guild.get_role(role_id)
        role_to_remove = ctx.guild.get_role(role_to_remove_id) if role_to_remove_id else None
        correct_emoji = random.choice(EMOJIS)

        embed = discord.Embed(title=titre, description=description, color=COLOR_DEFAULT)
        view = VerificationView(correct_emoji, None, role_to_give, role_to_remove, self.db, ctx.guild.id, button_text="Se vérifier")

        msg = await channel.send(embed=embed, view=view)
        # On stocke l'emoji pour le message
        self.db.data["verification"][str(ctx.guild.id)]["last_message"] = msg.id
        self.db.data["verification"][str(ctx.guild.id)]["last_emoji"] = correct_emoji
        self.db.save()
        await ctx.send(f"Embed de vérification envoyé dans {channel.mention}")

# ---------------- Setup ----------------
async def setup(bot):
    await bot.add_cog(Verification(bot))
