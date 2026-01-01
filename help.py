from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Aide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, page: str = None):
        pages = {
            "modération": "+kick, +ban, +mute, +unmute, +warn, +uwarn, +delwarn, +snipe",
            "giveaway": "+gyrole, +gyveaway, +gyend, +gyrestart",
            "fun": "+papa",
            "welcome": "+setwelcome, +setwelcomechannel",
            "logs": "+setlog"
        }
        if page and page.lower() in pages:
            await ctx.author.send(f"**{page.capitalize()} :**\n{pages[page.lower()]}")
        else:
            msg = "Pages disponibles : " + ", ".join(pages.keys())
            await ctx.author.send(msg)

def setup(bot):
    bot.add_cog(Aide(bot))
