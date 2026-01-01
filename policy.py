# policy.py
from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Policy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # Pour accéder à self.bot.db

    # Commande pour configurer le règlement
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reglement(
        self,
        ctx,
        titre,
        texte,
        role: discord.Role = None,
        image="aucun",
        emoji="aucun",
        texte_bouton="Accepter"
    ):
        """
        Configure le règlement du serveur.
        - titre : titre du règlement
        - texte : texte du règlement
        - role : rôle à donner après acceptation (facultatif)
        - image : URL de l'image (facultatif)
        - emoji : emoji pour le bouton (facultatif)
        - texte_bouton : texte du bouton
        """
        guild_id = ctx.guild.id
        role_id = role.id if role else None

        # Sauvegarde dans la DB
        self.bot.db.set_rule(guild_id, titre, texte, role_id, texte_bouton, emoji)

        # Création de l'embed
        embed = discord.Embed(title=titre, description=texte, color=COLOR)
        if image != "aucun":
            embed.set_image(url=image)

        # Création du bouton
        class AcceptButton(discord.ui.View):
            def __init__(self):
                super().__init__()
                button_emoji = emoji if emoji != "aucun" else None
                self.add_item(
                    discord.ui.Button(
                        label=texte_bouton,
                        style=discord.ButtonStyle.green,
                        emoji=button_emoji,
                        custom_id="accept_rule"
                    )
                )

            @discord.ui.button(label=texte_bouton, style=discord.ButtonStyle.green, custom_id="accept_rule", emoji=emoji if emoji != "aucun" else None)
            async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
                rule = self.bot.db.get_rule(ctx.guild.id)
                role_to_give = rule.get("role")
                if role_to_give:
                    member = interaction.user
                    discord_role = ctx.guild.get_role(role_to_give)
                    if discord_role and discord_role not in member.roles:
                        await member.add_roles(discord_role)
                await interaction.response.send_message("✅ Vous avez accepté le règlement.", ephemeral=True)

        # Envoi dans le salon actuel
        await ctx.send(embed=embed, view=AcceptButton())
        await ctx.send(f"Règlement configuré avec succès : **{titre}**")

# ✅ Setup pour Discord.py 2.x
async def setup(bot):
    await bot.add_cog(Policy(bot))
