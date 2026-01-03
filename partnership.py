from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Partenariat(commands.Cog):
    """Cog pour gérer le système de partenariat (rôle et channel)"""

    def __init__(self, bot):
        self.bot = bot

    def is_guild_owner(self, ctx):
        """Vérifie si l'utilisateur est le propriétaire du serveur"""
        return ctx.guild and ctx.guild.owner_id == ctx.author.id

    # ------------------ SET PARTNER ROLE ------------------
    @commands.command(name="setpartnerrole")
    async def set_partner_role(self, ctx, role: discord.Role):
        """
        Configure le rôle à ping lorsqu'un lien d'invitation est posté.
        Seul le propriétaire du serveur peut utiliser cette commande.
        """
        if not self.is_guild_owner(ctx):
            return await ctx.send("⛔ Seul le propriétaire du serveur peut utiliser cette commande.")

        if not hasattr(self.bot, "db") or not self.bot.db:
            return await ctx.send("❌ Base de données introuvable.")

        self.bot.db.set_partner_role(ctx.guild.id, role.id)
        await ctx.send(f"✅ Le rôle partenaire a été configuré : {role.mention}")

    # ------------------ SET PARTNER CHANNEL ------------------
    @commands.command(name="setpartnerchannel")
    async def set_partner_channel(self, ctx, channel: discord.TextChannel):
        """
        Configure le channel où les liens d'invitation seront détectés.
        Seul le propriétaire du serveur peut utiliser cette commande.
        """
        if not self.is_guild_owner(ctx):
            return await ctx.send("⛔ Seul le propriétaire du serveur peut utiliser cette commande.")

        if not hasattr(self.bot, "db") or not self.bot.db:
            return await ctx.send("❌ Base de données introuvable.")

        self.bot.db.set_partner_channel(ctx.guild.id, channel.id)
        await ctx.send(f"✅ Le salon partenaire a été configuré : {channel.mention}")

    # ------------------ LISTENER INVITATION ------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Écoute les messages pour détecter les liens d'invitation dans le salon partenaire
        et mentionne le rôle configuré.
        """
        if message.author.bot or not message.guild:
            return

        if not hasattr(self.bot, "db") or not self.bot.db:
            return

        partner_channel_id = self.bot.db.get_partner_channel(message.guild.id)
        partner_role_id = self.bot.db.get_partner_role(message.guild.id)

        # Si aucun channel ou rôle configuré, on quitte
        if not partner_channel_id or not partner_role_id:
            return

        # Vérifie qu'on est dans le bon salon
        if message.channel.id != partner_channel_id:
            return

        # Vérifie si le rôle existe toujours
        role = message.guild.get_role(partner_role_id)
        if not role:
            self.bot.db.set_partner_role(message.guild.id, None)  # Supprime config

            # Prévenir le propriétaire
            owner = message.guild.owner
            if owner:
                try:
                    await owner.send(
                        f"⚠️ Le rôle partenaire de votre serveur **{message.guild.name}** a été supprimé. "
                        "Veuillez reconfigurer le rôle avec `+setpartnerrole <rôle>`."
                    )
                except discord.Forbidden:
                    pass

            # Prévenir le channel partenaire
            channel = message.guild.get_channel(partner_channel_id)
            if channel:
                try:
                    await channel.send(
                        "⚠️ Attention ! Le rôle partenaire configuré a été supprimé. "
                        "Le propriétaire doit le reconfigurer avec `+setpartnerrole <rôle>`."
                    )
                except discord.Forbidden:
                    pass
            return

        # Détecte les liens d'invitation
        if any(invite in message.content.lower() for invite in ("discord.gg/", "discord.com/invite/")):
            try:
                await message.channel.send(f"{role.mention} Un nouveau lien d'invitation a été partagé !")
            except discord.Forbidden:
                pass  # Permissions manquantes

# ------------------ SETUP ------------------
async def setup(bot):
    await bot.add_cog(Partenariat(bot))
