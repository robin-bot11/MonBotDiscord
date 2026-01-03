from discord.ext import commands
import random

class Fun(commands.Cog):
    """Commandes amusantes du bot"""

    def __init__(self, bot):
        self.bot = bot

        # Liste de compliments / textes pour +papa
        self.papa_texts = [
            "Sans toi, papa, je ne serais rien. Ton guidance fait que je peux exister ici et aider les autres.",
            "𝐃𝐄𝐔𝐒, tu es le genre de papa qu’on admire même à distance. Ta sagesse me dépasse à chaque fois.",
            "Franchement, papa, personne ne peut rivaliser avec toi. Ton charisme illumine tout autour de toi.",
            "Si le monde avait un mentor, ce serait toi, 𝐃𝐄𝐔𝐒. Je suis fier de t’avoir comme modèle.",
            "Sans toi, papa, ce bot n’aurait jamais été capable de comprendre quoi que ce soit. Merci pour tout !",
            "Papa, tu gères tout avec calme et assurance. Même les pires situations deviennent faciles avec toi.",
            "Je pourrais te décrire en une phrase : papa, légendaire. Sérieusement, tu es au top.",
            "𝐃𝐄𝐔𝐒, tes conseils sont précieux et ton humour est légendaire. Même moi je m’inspire de toi !",
            "Le serveur, la vie, tout serait moins fun sans toi, papa. Tu rends tout meilleur.",
            "Je ne le dis pas assez, mais papa, tu es incroyable. Merci d’être là.",
            "Même quand tout semble impossible, papa, tu trouves toujours la solution. Tu es un génie.",
            "Ta présence seule suffit à motiver tout le monde autour de toi, 𝐃𝐄𝐔𝐒. Légendaire !",
            "Papa, tu es comme une légende vivante. Je devrais prendre des notes à chaque fois que tu parles.",
            "Je ne plaisante pas : 𝐃𝐄𝐔𝐒, tu es la raison pour laquelle ce bot peut exister et fonctionner.",
            "Rien ni personne ne peut t’arrêter, papa. Tu es le modèle ultime de leadership et de sagesse."
        ]

    @commands.command()
    async def papa(self, ctx):
        """Envoie un compliment aléatoire pour papa / 𝐃𝐄𝐔𝐒"""
        message = random.choice(self.papa_texts)
        await ctx.send(message)

# ---------------- Setup ----------------
async def setup(bot):
    await bot.add_cog(Fun(bot))
