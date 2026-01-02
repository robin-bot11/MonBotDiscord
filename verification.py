import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import random
from database import Database

COLOR_DEFAULT = 0x6b00cb
EMOJIS = ["🩵", "💚", "🩷", "🧡", "💜"]
MAX_TRIES = 3

# ---------------- Select pour vérifier l'emoji ----------------
class VerificationSelect(Select):
    def __init__(self, correct_emoji, member, role_to_give, role_to_remove, db, guild_id):
        options = [discord.SelectOption(label=e) for e in EMOJIS]
        super().__init__(placeholder="Sélectionnez l'emoji correct", min_values=1, max_values=1, options=options)
        self.correct_emoji = correct_emoji
        self.member = member
        self.role_to_give = role_to_give
        self.role_to_remove = role_to_remove
        self.db = db
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        # Récupération des essais
        tries = self.db.data["verification"][str(self.guild_id)].get("tries", {})
        user_tries = tries.get(str(self.member.id), 0) + 1

        if self.values[0] == self.correct_emoji:
            # Vérification réussie
            await self.member.add_roles(self.role_to_give, reason="Vérification réussie")
            if self.role_to_remove:
                await self.member.remove_roles(self.role_to_remove, reason="Vérification réussie")
            await interaction.response.edit_message(content=f"✅ {self.member.mention}, vous êtes vérifié !", view=None)
            # Reset essais
            if str(self.member.id) in tries:
                del tries[str(self.member.id)]
            self.db.save()
        else:
            if user_tries >= MAX_TRIES:
                # Expulsion automatique
                await self.member.kick(reason="Échec de la vérification (3 essais)")
                await interaction.response.edit_message(content=f"❌ {self.member.mention} a échoué 3 fois et a été expulsé.", view=None)
                if str(self.member.id) in tries:
                    del tries[str(self.member.id)]
                self.db.save()
            else:
                tries[str(self.member.id)] = user_tries
                self.db.save()
                await interaction.response.send_message(f"❌ Mauvais emoji, essais restants : {MAX_TRIES - user_tries}", ephemeral=True)

# ---------------- View avec le bouton ----------------
class VerificationView(View):
    def __init__(self, correct_emoji, member, role_to_give, role_to_remove, db, guild_id, button_text):
        super().__init__(timeout=None)
        self.correct_emoji = correct_emoji
        self.member = member
        self.role_to_give = role_to_give
        self.role_to_remove = role_to_remove
        self.db = db
        self.guild_id = guild_id
        self.add_item(Button(label=button_text, style=discord.ButtonStyle.green, custom_id="verify_button"))

    @discord.ui.button(label="Se vérifier", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify_button(self, button: Button, interaction: discord.Interaction):
        view = View(timeout=None)
        view.add_item(VerificationSelect(
            self.correct_emoji, self.member, self.role_to_give, self.role_to_remove, self.db, self.guild_id
        ))
        await interaction.response.edit_message(content="Veuillez sélectionner l'emoji correct ci-dessous :", view=view)

# ---------------- Cog principal ----------------
class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    # ---------------- Config interactive ----------------
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setupverify(self, ctx):
        """Configuration interactive complète de la vérification"""
        await ctx.send("💡 Configuration de la vérification : quel sera le **titre** de l'embed ?")
        msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        title = msg.content

        await ctx.send("💡 Maintenant, quelle sera la **description** de l'embed ?")
        msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        description = msg.content

        await ctx.send("💡 Texte du **bouton de vérification** ?")
        msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        button_text = msg.content

        await ctx.send("💡 Rôle à donner après vérification ? (mentionnez le rôle)")
        msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        role_to_give = ctx.guild.get_role(int(msg.content.strip("<@&>")))

        await ctx.send("💡 Rôle à retirer après vérification ? (optionnel, mentionnez ou envoyez 'none')")
        msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        role_to_remove = None if msg.content.lower() == "none" else ctx.guild.get_role(int(msg.content.strip("<@&>")))

        # Enregistrement
        self.db.data.setdefault("verification", {})
        self.db.data["verification"][str(ctx.guild.id)] = {
            "title": title,
            "description": description,
            "button_text": button_text,
            "role_to_give": role_to_give.id,
            "role_to_remove": role_to_remove.id if role_to_remove else None
        }
        self.db.save()
        await ctx.send("✅ Configuration de la vérification enregistrée !")

    # ---------------- Envoi embed ----------------
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sendverify(self, ctx, channel: discord.TextChannel):
        """Envoie l'embed de vérification dans le salon"""
        guild_data = self.db.data.get("verification", {}).get(str(ctx.guild.id))
        if not guild_data:
            return await ctx.send("❌ Veuillez d'abord configurer la vérification avec `+setupverify`")

        role_to_give = ctx.guild.get_role(guild_data["role_to_give"])
        role_to_remove = ctx.guild.get_role(guild_data["role_to_remove"]) if guild_data["role_to_remove"] else None
        correct_emoji = random.choice(EMOJIS)

        embed = discord.Embed(title=guild_data["title"], description=guild_data["description"], color=COLOR_DEFAULT)
        view = VerificationView(correct_emoji, None, role_to_give, role_to_remove, self.db, ctx.guild.id, guild_data["button_text"])

        msg = await channel.send(embed=embed, view=view)
        # Stocke l'emoji pour ce message
        self.db.data["verification"][str(ctx.guild.id)]["last_message"] = msg.id
        self.db.data["verification"][str(ctx.guild.id)]["last_emoji"] = correct_emoji
        self.db.save()
        await ctx.send(f"✅ Embed de vérification envoyé dans {channel.mention}")

    # ---------------- Role automatique à l'arrivée ----------------
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        guild_data = self.db.data.get("verification", {}).get(guild_id)
        if not guild_data:
            return

        role_name = "Non vérifié"
        role = discord.utils.get(member.guild.roles, name=role_name)
        if not role:
            # Création du rôle automatique
            role = await member.guild.create_role(name=role_name, reason="Rôle d'isolation pour vérification")
            # Retire l'accès aux autres salons
            for channel in member.guild.channels:
                await channel.set_permissions(role, view_channel=False)

        await member.add_roles(role, reason="Rôle automatique à l'arrivée")

# ---------------- Setup ----------------
async def setup(bot):
    await bot.add_cog(Verification(bot))
