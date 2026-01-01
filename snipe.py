from discord.ext import commands

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_deleted = None

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot:
            self.last_deleted = message

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def snipe(self, ctx):
        if self.last_deleted:
            await ctx.send(f"Dernier message supprimé : {self.last_deleted.content}")
        else:
            await ctx.send("Rien à snipe pour le moment !")

def setup(bot):
    bot.add_cog(Snipe(bot))
