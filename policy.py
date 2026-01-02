# policy.py
from discord.ext import commands
import discord
from storx import Database  # ← Correction ici

COLOR = 0x6b00cb

class Policy(commands.Cog):
    """Gestion du règlement avec embed et bouton d'acceptation."""

    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reglement(self, ctx):
        """Assistant configuration du règlement étape par étape."""
        def check(m): return m.author == ctx.author and m.channel == ctx.channel

        # Titre
        await ctx.send("📄 **Titre du règlement :**")
        try: msg = await self.bot.wait_for("message", check=check, timeout=120); title=msg.content
        except: return await ctx.send("⏱️ Temps écoulé.")

        # Texte
        await ctx.send("✏️ **Texte complet :**")
        try: msg = await self.bot.wait_for("message", check=check, timeout=300); text=msg.content
        except: return await ctx.send("⏱️ Temps écoulé.")

        # Rôle
        await ctx.send("👤 **Rôle à donner après acceptation ?** (ou `n` pour aucun)")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
            if msg.content.lower() == "n": role_id=None
            else:
                role = discord.utils.get(ctx.guild.roles, name=msg.content) or ctx.guild.get_role(int(msg.content))
                if not role: return await ctx.send("❌ Rôle non trouvé.")
                role_id = role.id
        except: return await ctx.send("⏱️ Temps écoulé.")

        # Texte du bouton
        await ctx.send("✅ **Texte bouton :**")
        try: msg = await self.bot.wait_for("message", check=check, timeout=60); button_text=msg.content
        except: return await ctx.send("⏱️ Temps écoulé.")

        # Emoji
        await ctx.send("🔢 **Emoji :** (ou `n` pour aucun)")
        try: msg = await self.bot.wait_for("message", check=check, timeout=60)
        emoji = None if msg.content.lower()=="n" else msg.content
        except: return await ctx.send("⏱️ Temps écoulé.")

        # Image
        await ctx.send("🖼️ **Image :** (ou `n` pour aucune)")
        try: msg = await self.bot.wait_for("message", check=check, timeout=120)
        image = None if msg.content.lower()=="n" else msg.content
        except: return await ctx.send("⏱️ Temps écoulé.")

        # Sauvegarde
        self.db.set_rule(ctx.guild.id, title, text, role_id, button_text, emoji, image)
        await ctx.send("✅ Règlement configuré !")

    @commands.command()
    async def showreglement(self, ctx):
        """Affiche le règlement avec le bouton d'acceptation."""
        data = self.db.get_rule(ctx.guild.id)
        if not data: return await ctx.send("❌ Aucun règlement configuré.")
        embed = discord.Embed(title=data.get("title","Règlement"), description=data.get("text",""), color=COLOR)
        if data.get("image"): embed.set_image(url=data["image"])

        class AcceptButton(discord.ui.View):
            def __init__(self, role_id, button_text, emoji):
                super().__init__(timeout=None)
                self.role_id = role_id
                self.button_text = button_text or "Accepter"
                self.emoji = emoji
                self.add_item(discord.ui.Button(label=self.button_text, style=discord.ButtonStyle.green, emoji=self.emoji))

            @discord.ui.button(label="Accepter", style=discord.ButtonStyle.green)
            async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
                role = interaction.guild.get_role(self.role_id) if self.role_id else None
                if role and role in interaction.user.roles:
                    await interaction.response.send_message("✅ Déjà accepté.", ephemeral=True)
                else:
                    if role: await interaction.user.add_roles(role); await interaction.response.send_message(f"✅ Accepté et reçu {role.name}.", ephemeral=True)
                    else: await interaction.response.send_message("✅ Accepté.", ephemeral=True)

        view = AcceptButton(data.get("role"), data.get("button"), data.get("emoji"))
        await ctx.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        for guild_id in self.db.get_all_rule_guilds():
            data=self.db.get_rule(guild_id)
            if data and data.get("role")==role.id:
                guild=self.bot.get_guild(int(guild_id))
                if not guild: continue
                owner=guild.owner
                if owner:
                    try: await owner.send(f"⚠️ Le rôle `{role.name}` a été supprimé dans **{guild.name}**. Reconfigurez-le.")
                    except: pass
                if guild.system_channel:
                    await guild.system_channel.send("⚠️ Rôle du règlement supprimé. Reconfigurez-le.")
                self.db.set_rule(guild.id,data["title"],data["text"],None,data["button"],data["emoji"],data["image"])

async def setup(bot):
    await bot.add_cog(Policy(bot))
