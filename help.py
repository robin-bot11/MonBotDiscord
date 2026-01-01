from discord.ext import commands
import discord

COLOR = 0x6b00cb

class Aide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, page=None):
        pages = {
            "modération": "+kick <ID> <raison>\n+ban <ID> <raison>\n+uban <ID>\n+mute <ID> <durée> <raison>\n+umute <ID>\n+warn <ID> <raison>\n+warns <ID>\n+delswarn <ID> <num>",
            "fun": "+papa",
            "giveaway": "+gyrole <ID rôle>\n+gyveaway <durée> <récompense>\n+gyend <ID>\n+gyrestart <ID>",
            "bienvenue": "+setwelcome <message>\n+setwelcomechannel <#salon>",
            "logs": "+setlog <type> <#salon>",
            "règlement": "+reglement"
        }
        if page and page.lower() in pages:
            await ctx.author.send(f"Page {page} :\n{pages[page.lower()]}")
        else:
            desc = "\n".join([f"{k}" for k in pages])
            await ctx.author.send(f"Pages d'aide disponibles :\n{desc}")

def setup(bot):
    bot.add_cog(Aide(bot))
