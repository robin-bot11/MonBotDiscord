# policy.py
from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Policy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # accès à self.bot.db

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setreglement(self, ctx, title: str, role: discord.Role, button_text: str, emoji: str = None, *, text: str):
        """
        Configure le règlement du serveur.
        Exemple :
        +setreglement "Règles" @Membre "Accepter" ✅ "Le texte complet des règles ici"
        """
        self.bot.db.set_rule(ctx.guild.id, title, text, role.id, button_text, emoji or "✅")
        await ctx.send(f"✅ Règlement configuré avec succès pour le rôle {role.mention}.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reglement(self, ctx):
        """
        Envoie le règlement avec le bouton pour accepter.
        """
        data = self.bot.db.get_rule(ctx.guild.id)
        if not data:
            return await ctx.send("❌ Aucun règlement configuré pour ce serveur.")

        embed = discord.Embed(
            title=data["title"],
            description=data["text"],
            color=COLOR
        )

        # Création du bouton
        class AcceptButton(discord.ui.View):
            def __init__(self, role_id, emoji):
                super().__init__(timeout=None)
                self.role_id = role_id
                self.emoji = emoji

            @discord.ui.button(label=data["button"], style=discord.ButtonStyle.green, emoji=data["emoji"])
            async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
                role = interaction.guild.get_role(self.role_id)
                if not role:
                    return await interaction.response.send_message("❌ Rôle non trouvé.", ephemeral=True)
                if role in interaction.user.roles:
                    return await interaction.response.send_message("✅ Vous avez déjà accepté le règlement.", ephemeral=True)
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"✅ Vous avez accepté le règlement et reçu le rôle {role.name}.", ephemeral=True)

        view = AcceptButton(data["role"], data["emoji"])
        await ctx.send(embed=embed, view=view)

# ✅ Correct pour Discord.py 2.x
async def setup(bot):
    await bot.add_cog(Policy(bot))
