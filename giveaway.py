from discord.ext import commands

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_roles = []  # Rôles autorisés à lancer des giveaways

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def gyrole(self, ctx, role_id: int):
        role = ctx.guild.get_role(role_id)
        if role:
            self.allowed_roles.append(role.id)
            await ctx.send(f"Rôle {role.name} autorisé à lancer des giveaways.")
        else:
            await ctx.send("Rôle introuvable.")

    @commands.command()
    async def gyveaway(self, ctx, duree, *, recompense):
        if any(role.id in self.allowed_roles for role in ctx.author.roles) or ctx.author.guild_permissions.administrator:
            await ctx.send(f"Giveaway lancé pour {recompense} pendant {duree}.")
        else:
            await ctx.send("Vous n'avez pas la permission de lancer un giveaway.")

    @commands.command()
    async def gyend(self, ctx, giveaway_id: int):
        await ctx.send(f"Giveaway {giveaway_id} terminé.")

    @commands.command()
    async def gyrestart(self, ctx, giveaway_id: int):
        await ctx.send(f"Giveaway {giveaway_id} relancé.")

def setup(bot):
    bot.add_cog(Giveaway(bot))
