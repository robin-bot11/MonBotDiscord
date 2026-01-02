# Verification.py
from discord.ext import commands
import discord
import random
from database import Database

COLOR_DEFAULT = 0x6b00cb
CAPTCHA_EMOJIS = ["🩵","💚","🩷","🧡","💜"]  # uniquement pour le captcha

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.active_captchas = {}

    # ------------------ Assistant de configuration ------------------
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setupverif(self, ctx):
        """Assistant interactif pour configurer la vérification."""
        guild = ctx.guild

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send("Assistant de configuration de la vérification. Répondez aux questions.")

        # Rôle à donner après vérification
        await ctx.send("Quel rôle faut-il donner une fois la vérification passée ? (mention ou ID)")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
            role_verified = await commands.RoleConverter().convert(ctx, msg.content)
        except:
            return await ctx.send("Rôle invalide ou temps écoulé. Configuration annulée.")

        # Rôle à retirer après vérification (optionnel)
        await ctx.send("Quel rôle faut-il retirer une fois la vérification passée ? (mention, ID ou 'none')")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
            if msg.content.lower() == "none":
                role_unverified = None
            else:
                role_unverified = await commands.RoleConverter().convert(ctx, msg.content)
        except:
            return await ctx.send("Rôle invalide ou temps écoulé. Configuration annulée.")

        # Création automatique du rôle non vérifié si aucun
        if not role_unverified:
            role_unverified = await guild.create_role(
                name="Non Vérifié",
                mentionable=False,
                reason="Rôle créé automatiquement pour la vérification"
            )
            for ch in guild.channels:
                await ch.set_permissions(role_unverified, read_messages=False, send_messages=False, speak=False)

        # Embed
        await ctx.send("Quel titre pour l'embed ?")
        try:
            title = (await self.bot.wait_for("message", check=check, timeout=120)).content
        except:
            return await ctx.send("Temps écoulé. Configuration annulée.")

        await ctx.send("Quelle description pour l'embed ?")
        try:
            description = (await self.bot.wait_for("message", check=check, timeout=300)).content
        except:
            return await ctx.send("Temps écoulé. Configuration annulée.")

        # Bouton
        await ctx.send("Quel texte pour le bouton ?")
        try:
            button_text = (await self.bot.wait_for("message", check=check, timeout=120)).content
        except:
            return await ctx.send("Temps écoulé. Configuration annulée.")

        await ctx.send("Quelle couleur pour le bouton ? (hex, ex: #6b00cb ou 'default')")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
            button_color = COLOR_DEFAULT if msg.content.lower() == "default" else int(msg.content.replace("#",""),16)
        except:
            return await ctx.send("Valeur invalide. Configuration annulée.")

        # Emoji captcha
        await ctx.send(f"Choisissez un emoji pour le captcha parmi : {', '.join(CAPTCHA_EMOJIS)}")
        try:
            captcha_emoji = (await self.bot.wait_for("message", check=check, timeout=60)).content
            if captcha_emoji not in CAPTCHA_EMOJIS:
                return await ctx.send("Emoji invalide. Configuration annulée.")
        except:
            return await ctx.send("Temps écoulé. Configuration annulée.")

        # Sauvegarde
        self.db.data.setdefault("verification", {})
        self.db.data["verification"][str(guild.id)] = {
            "role_verified": role_verified.id,
            "role_unverified": role_unverified.id,
            "embed_title": title,
            "embed_desc": description,
            "button_text": button_text,
            "button_color": button_color,
            "captcha_emoji": captcha_emoji,
            "channel_id": None
        }
        self.db.save()
        await ctx.send("Configuration terminée. Utilisez `+sendverif` pour envoyer l'embed dans un salon.")

    # ------------------ Envoi de l'embed ------------------
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sendverif(self, ctx, channel: discord.TextChannel):
        guild_id = str(ctx.guild.id)
        cfg = self.db.data.get("verification", {}).get(guild_id)
        if not cfg:
            return await ctx.send("Aucune configuration trouvée. Faites `+setupverif` d'abord.")

        # Enregistrement du salon
        self.db.data["verification"][guild_id]["channel_id"] = channel.id
        self.db.save()

        # Bouton
        class VerifButton(discord.ui.View):
            def __init__(self, bot, cfg):
                super().__init__(timeout=None)
                self.bot = bot
                self.cfg = cfg
                self.add_item(discord.ui.Button(
                    label=cfg["button_text"],
                    style=discord.ButtonStyle.primary,
                    custom_id="verif_button"
                ))

        embed = discord.Embed(title=cfg["embed_title"], description=cfg["embed_desc"], color=cfg["button_color"])
        await channel.send(embed=embed, view=VerifButton(self.bot, cfg))
        await ctx.send(f"Embed de vérification envoyé dans {channel.mention}.")

    # ------------------ Gestion des interactions ------------------
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return
        if interaction.data.get("custom_id") != "verif_button":
            return

        guild_id = str(interaction.guild.id)
        cfg = self.db.data.get("verification", {}).get(guild_id)
        if not cfg:
            await interaction.response.send_message("Configuration introuvable.", ephemeral=True)
            return

        member = interaction.user
        captcha_emoji = cfg["captcha_emoji"]

        # Mélange des emojis pour le menu
        emojis = [captcha_emoji] + [e for e in CAPTCHA_EMOJIS if e != captcha_emoji]
        random.shuffle(emojis)

        class EmojiSelect(discord.ui.View):
            def __init__(self, bot, cfg, member):
                super().__init__(timeout=60)
                self.bot = bot
                self.cfg = cfg
                self.member = member
                for e in emojis:
                    self.add_item(discord.ui.Button(label=e, style=discord.ButtonStyle.secondary, custom_id=f"emoji_{e}"))

            async def interaction_check(self, inter):
                return inter.user.id == self.member.id

        view = EmojiSelect(self.bot, cfg, member)
        await interaction.response.send_message("Choisissez le bon emoji :", view=view, ephemeral=True)

        # Gestion clic emoji
        async def wait_for_emoji():
            while True:
                try:
                    i = await self.bot.wait_for("interaction", check=lambda inter: inter.user.id == member.id and inter.data.get("custom_id","").startswith("emoji_"), timeout=60)
                    selected = i.data["custom_id"].split("_")[1]
                    role_verified = interaction.guild.get_role(cfg["role_verified"])
                    role_unverified = interaction.guild.get_role(cfg["role_unverified"])
                    if selected == captcha_emoji:
                        await member.add_roles(role_verified)
                        if role_unverified in member.roles:
                            await member.remove_roles(role_unverified)
                        await i.response.send_message("Vérification réussie ! Rôle attribué.", ephemeral=True)
                        break
                    else:
                        await i.response.send_message("Mauvais emoji, réessayez.", ephemeral=True)
                except:
                    break

        self.bot.loop.create_task(wait_for_emoji())


# ------------------ Setup ------------------
async def setup(bot):
    await bot.add_cog(Verification(bot))
