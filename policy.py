from discord.ext import commands
import discord
from storx import Database  # Correction ici
COLOR = 0x6b00cb

class Policy(commands.Cog):
    """Gestion du règlement avec embed et bouton d'acceptation."""

    def __init__(self, bot):
        self.bot = bot
        self.db = Database()  # Pour stocker le règlement

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reglement(self, ctx):
        """Assistant pour configurer le règlement étape par étape."""
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        # 1️⃣ Titre
        await ctx.send("📄 **Entrez le titre du règlement :**")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
            title = msg.content
        except:
            return await ctx.send("⏱️ Temps écoulé.")

        # 2️⃣ Texte
        await ctx.send("✏️ **Entrez le texte complet du règlement :**")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=300)
            text = msg.content
        except:
            return await ctx.send("⏱️ Temps écoulé.")

        # 3️⃣ Rôle
        await ctx.send("👤 **Quel rôle donner après acceptation ?** (ou tapez `n` pour aucun)")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
            if msg.content.lower() == "n":
                role_id = None
            else:
                role = discord.utils.get(ctx.guild.roles, name=msg.content) or ctx.guild.get_role(int(msg.content))
                if not role:
                    return await ctx.send("❌ Rôle non trouvé.")
                role_id = role.id
        except:
            return await ctx.send("⏱️ Temps écoulé.")

        # 4️⃣ Texte du bouton
        await ctx.send("✅ **Texte du bouton pour accepter le règlement :**")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            button_text = msg.content
        except:
            return await ctx.send("⏱️ Temps écoulé.")

        # 5️⃣ Emoji du bouton
        await ctx.send("🔢 **Emoji pour le bouton :** (ou `n` pour aucun)")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            emoji = None if msg.content.lower() == "n" else msg.content
        except:
            return await ctx.send("⏱️ Temps écoulé.")

        # 6️⃣ Image
        await ctx.send("🖼️ **Image à mettre dans l'embed ?** (ou `n` pour aucune)")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
            image = None if msg.content.lower() == "n" else msg.content
        except:
            return await ctx.send("⏱️ Temps écoulé.")

        # Sauvegarde dans la DB
        self.db.set_rule(ctx.guild.id, title, text, role_id, button_text, emoji, image)
        await ctx.send("✅ **Règlement configuré avec succès !**")

    @commands.command()
    async def showreglement(self, ctx):
        """Affiche le règlement avec le bouton d'acceptation."""
        data = self.db.get_rule(ctx.guild.id)
        if not data:
            return await ctx.send("❌ Aucun règlement configuré pour ce serveur.")

        embed = discord.Embed(
            title=data.get("title", "Règlement"),
            description=data.get("text", ""),
            color=COLOR
        )
        if data.get("image"):
            embed.set_image(url=data["image"])

        class AcceptButton(discord.ui.View):
            def __init__(self, role_id, button_text, emoji):
                super().__init__(timeout=None)
                self.role_id = role_id
                self.button_text = button_text or "Accepter"
                self.emoji = emoji
                self.add_item(discord.ui.Button(label=self.button_text, style=discord.ButtonStyle.green, emoji=self.emoji))

            @discord.ui.button(label="placeholder", style=discord.ButtonStyle.green, disabled=True)
            async def placeholder(self, interaction: discord.Interaction, button: discord.ui.Button):
                pass

            @discord.ui.button(label="Accepter", style=discord.ButtonStyle.green)
            async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
                role = interaction.guild.get_role(self.role_id) if self.role_id else None
                if role and role in interaction.user.roles:
                    await interaction.response.send_message("✅ Vous avez déjà accepté le règlement.", ephemeral=True)
                else:
                    if role:
                        await interaction.user.add_roles(role)
                        await interaction.response.send_message(f"✅ Vous avez accepté le règlement et reçu le rôle {role.name}.", ephemeral=True)
                    else:
                        await interaction.response.send_message("✅ Vous avez accepté le règlement.", ephemeral=True)

        view = AcceptButton(data.get("role"), data.get("button"), data.get("emoji"))
        await ctx.send(embed=embed, view=view)

    # ---------------- Listener pour rôle supprimé ----------------
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        # Vérifie si le rôle supprimé est utilisé pour le règlement
        for guild_id in self.db.get_all_rule_guilds():  # Méthode à créer si nécessaire
            data = self.db.get_rule(guild_id)
            if data and data.get("role") == role.id:
                guild = self.bot.get_guild(int(guild_id))
                if not guild:
                    continue
                owner = guild.owner
                # DM au propriétaire
                if owner:
                    try:
                        await owner.send(
                            f"⚠️ Le rôle d'acceptation du règlement (`{role.name}`) a été supprimé dans **{guild.name}**. Veuillez le reconfigurer."
                        )
                    except:
                        pass
                # Message dans le channel principal (si possible)
                if guild.system_channel:
                    await guild.system_channel.send(
                        f"⚠️ Le rôle d'acceptation du règlement a été supprimé. Veuillez reconfigurer le règlement pour que les membres puissent l'accepter."
                    )
                # Supprime le rôle de la config DB pour éviter les erreurs
                self.db.set_rule(guild.id, data["title"], data["text"], None, data["button"], data["emoji"], data["image"])

async def setup(bot):
    await bot.add_cog(Policy(bot))
