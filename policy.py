# policy.py
from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Policy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # accès à self.bot.db

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reglement(self, ctx):
        """Assistant pour configurer le règlement étape par étape."""
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send("📄 **Entrez le titre du règlement :**")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
            title = msg.content
        except:
            return await ctx.send("⏱️ Temps écoulé.")

        await ctx.send("✏️ **Entrez le texte complet du règlement :**")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=300)
            text = msg.content
        except:
            return await ctx.send("⏱️ Temps écoulé.")

        await ctx.send("👤 **Quel rôle donner après acceptation ?** (ou tapez `n` pour ne pas donner de rôle)")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
            if msg.content.lower() == "n":
                role_id = None
            else:
                role = discord.utils.get(ctx.guild.roles, name=msg.content) or discord.utils.get(ctx.guild.roles, id=int(msg.content))
                if not role:
                    return await ctx.send("❌ Rôle non trouvé.")
                role_id = role.id
        except:
            return await ctx.send("⏱️ Temps écoulé.")

        await ctx.send("✅ **Texte du bouton pour accepter le règlement :**")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            button_text = msg.content
        except:
            return await ctx.send("⏱️ Temps écoulé.")

        await ctx.send("🔢 **Emoji pour le bouton :** (ou `n` pour aucun)")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            emoji = None if msg.content.lower() == "n" else msg.content
        except:
            return await ctx.send("⏱️ Temps écoulé.")

        await ctx.send("🖼️ **Image à mettre dans l'embed ?** (ou `n` pour aucune)")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
            if msg.content.lower() == "n":
                image = None
            else:
                image = msg.content  # on prend le lien
        except:
            return await ctx.send("⏱️ Temps écoulé.")

        # Sauvegarde dans la base
        self.bot.db.set_rule(ctx.guild.id, title, text, role_id, button_text, emoji, image)

        await ctx.send("✅ **Règlement configuré avec succès !**")

    @commands.command()
    async def showreglement(self, ctx):
        """Affiche le règlement avec le bouton d'acceptation."""
        data = self.bot.db.get_rule(ctx.guild.id)
        if not data:
            return await ctx.send("❌ Aucun règlement configuré pour ce serveur.")

        embed = discord.Embed(
            title=data["title"],
            description=data["text"],
            color=COLOR
        )
        if data.get("image"):
            embed.set_image(url=data["image"])

        class AcceptButton(discord.ui.View):
            def __init__(self, role_id, button_text, emoji):
                super().__init__(timeout=None)
                self.role_id = role_id
                self.button_text = button_text
                self.emoji = emoji

            @discord.ui.button(label="Accepter", style=discord.ButtonStyle.green)
            async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
                role = interaction.guild.get_role(self.role_id) if self.role_id else None
                if role and role in interaction.user.roles:
                    return await interaction.response.send_message("✅ Vous avez déjà accepté le règlement.", ephemeral=True)
                if role:
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message(f"✅ Vous avez accepté le règlement et reçu le rôle {role.name}.", ephemeral=True)
                else:
                    await interaction.response.send_message("✅ Vous avez accepté le règlement.", ephemeral=True)

        view = AcceptButton(data.get("role"), data.get("button"), data.get("emoji"))
        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Policy(bot))
