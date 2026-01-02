# welcome.py
from discord.ext import commands
import discord

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # Accès à self.bot.db

    # Commande pour définir le salon de bienvenue
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcomechannel(self, ctx, channel: discord.TextChannel):
        """Configurer le salon pour le message de bienvenue"""
        guild_id = str(ctx.guild.id)
        self.bot.db.set_welcome_channel(guild_id, channel.id)
        await ctx.send(f"✅ Salon de bienvenue défini : {channel.mention}")

    # Commande pour définir le message de bienvenue personnalisé
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcome(self, ctx, *, message):
        """
        Configurer le message de bienvenue.
        Vous pouvez utiliser :
        {user}    -> pour mentionner le membre
        {server}  -> pour le nom du serveur
        {members} -> pour le nombre de membres
        Exemple : "Bienvenue {user} sur {server}, nous sommes {members} !"
        """
        guild_id = str(ctx.guild.id)
        self.bot.db.set_welcome_message(guild_id, message)
        await ctx.send("✅ Message de bienvenue configuré !")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        welcome_cfg = self.bot.db.get_welcome(guild_id)
        channel_id = welcome_cfg.get("channel")
        message = welcome_cfg.get("message")

        if not channel_id:
            return  # Aucun salon défini
        channel = member.guild.get_channel(channel_id)
        if not channel:
            return  # Salon introuvable

        # Message par défaut si aucun message configuré
        if not message:
            message = "Souhaitez la bienvenue à {user} sur **{server} !**\nNous sommes maintenant {members} sur le serveur !!"

        # Remplacement des variables
        msg = message.format(
            user=member.mention,
            server=member.guild.name,
            members=member.guild.member_count
        )
        await channel.send(msg)

# ✅ Correct pour Discord.py 2.x
async def setup(bot):
    await bot.add_cog(Welcome(bot))
