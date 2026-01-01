from discord.ext import commands

class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reglement(self, ctx, titre, texte, role: str):
        role_msg = f"Rôle à attribuer: {role}" if role.lower() != "aucun" else "Pas de rôle attribué"
        await ctx.send(f"**{titre}**\n{texte}\n{role_msg}")

def setup(bot):
    bot.add_cog(Rules(bot))
