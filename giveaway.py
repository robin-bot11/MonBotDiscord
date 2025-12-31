from discord.ext import commands
import discord

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles_allowed = []

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def gyrole(self, ctx, role: discord.Role):
        if role.id not in self.roles_allowed:
            self.roles_allowed.append(role.id)
        await ctx.send(embed=discord.Embed(
            description=f"Rôle {role.name} autorisé à lancer des giveaways.",
            color=0x6b00cb
        ))

    @commands.command()
    async def gyveaway(self, ctx, durée, *, récompense):
        # Vérifier si le membre a un rôle autorisé
        if not any(r.id in self.roles_allowed for r in ctx.author.roles):
            await ctx.send(embed=discord.Embed(
                description="Vous n'avez pas le rôle pour lancer un giveaway.",
                color=0x6b00cb
            ))
            return
        await ctx.send(embed=discord.Embed(
            description=f"Giveaway lancé pour {récompense} durant {durée}.",
            color=0x6b00cb
        ))

    @commands.command()
    async def gyend(self, ctx, giveaway_id):
        await ctx.send(embed=discord.Embed(
            description=f"Giveaway {giveaway_id} terminé.",
            color=0x6b00cb
        ))

    @commands.command()
    async def gyrestart(self, ctx, giveaway_id):
        await ctx.send(embed=discord.Embed(
            description=f"Giveaway {giveaway_id} relancé.",
            color=0x6b00cb
        ))

def setup(bot):
    bot.add_cog(Giveaway(bot))
