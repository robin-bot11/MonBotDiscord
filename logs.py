from discord.ext import commands

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        print(f"[MESSAGE] {message.author}: {message.content}")

def setup(bot):
    bot.add_cog(Logs(bot))
