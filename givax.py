import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import random
import json
import os
import re

COLOR = 0x6b00cb
DATA_FILE = "giveaways.json"


# ---------- UTILS ----------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def parse_duration(text: str):
    text = text.lower().replace(" ", "")
    regex = r"(\d+)(j|jour|jours|h|heure|heures|m|minute|minutes|s|seconde|secondes)"
    matches = re.findall(regex, text)

    if not matches:
        return None

    seconds = 0
    for value, unit in matches:
        value = int(value)
        if unit.startswith("j"):
            seconds += value * 86400
        elif unit.startswith("h"):
            seconds += value * 3600
        elif unit.startswith("m"):
            seconds += value * 60
        elif unit.startswith("s"):
            seconds += value

    return seconds if seconds > 0 else None


# ---------- COG ----------

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    # ---------- CREATE ----------

    @commands.command()
    async def gyveaway(self, ctx, duration: str, winners: int, *, prize: str):
        seconds = parse_duration(duration)
        if not seconds or winners <= 0:
            return await ctx.send("❌ Utilisation : `+gyveaway 1j 2 Nitro`")

        end_time = datetime.utcnow() + timedelta(seconds=seconds)

        embed = discord.Embed(
            title="🎉 GIVEAWAY 🎉",
            description=(
                f"🎁 **Prix :** {prize}\n"
                f"🎯 **Gagnants :** {winners}\n"
                f"👥 **Participants :** 0\n\n"
                f"⏳ **Fin :** <t:{int(end_time.timestamp())}:R>\n"
                f"👤 **Organisé par :** {ctx.author.mention}"
            ),
            color=COLOR
        )

        view = discord.ui.View(timeout=None)
        button = discord.ui.Button(emoji="🎉", style=discord.ButtonStyle.primary)

        async def button_callback(interaction: discord.Interaction):
            gid = str(message.id)
            users = self.data[gid]["participants"]

            if interaction.user.id in users:
                return await interaction.response.send_message(
                    "❌ Tu participes déjà.", ephemeral=True
                )

            users.append(interaction.user.id)
            save_data(self.data)

            embed.description = embed.description.replace(
                f"👥 **Participants :** {len(users)-1}",
                f"👥 **Participants :** {len(users)}"
            )
            await message.edit(embed=embed)
            await interaction.response.send_message("✅ Participation enregistrée !", ephemeral=True)

        button.callback = button_callback
        view.add_item(button)

        message = await ctx.send(embed=embed, view=view)

        self.data[str(message.id)] = {
            "channel": ctx.channel.id,
            "prize": prize,
            "end": end_time.timestamp(),
            "participants": [],
            "winners": winners,
            "ended": False
        }
        save_data(self.data)

    # ---------- END ----------

    @commands.command()
    async def gyend(self, ctx, message_id: int):
        if str(message_id) not in self.data:
            return await ctx.send("❌ Giveaway introuvable.")

        self.data[str(message_id)]["end"] = datetime.utcnow().timestamp()
        save_data(self.data)
        await ctx.send("🛑 Giveaway terminé.")

    # ---------- RESTART ----------

    @commands.command()
    async def gyrestart(self, ctx, message_id: int, duration: str):
        if str(message_id) not in self.data:
            return await ctx.send("❌ Giveaway introuvable.")

        seconds = parse_duration(duration)
        if not seconds:
            return await ctx.send("❌ Durée invalide.")

        self.data[str(message_id)]["end"] = (
            datetime.utcnow() + timedelta(seconds=seconds)
        ).timestamp()
        self.data[str(message_id)]["ended"] = False
        save_data(self.data)

        await ctx.send("🔁 Giveaway relancé.")

    # ---------- LOOP ----------

    @tasks.loop(seconds=5)
    async def check_giveaways(self):
        now = datetime.utcnow().timestamp()

        for gid, gw in list(self.data.items()):
            if gw["ended"] or now < gw["end"]:
                continue

            channel = self.bot.get_channel(gw["channel"])
            if not channel:
                continue

            participants = gw["participants"]
            winners_count = gw["winners"]

            if not participants:
                result = "❌ Aucun participant."
            else:
                selected = random.sample(
                    participants,
                    min(len(participants), winners_count)
                )
                result = "🏆 " + ", ".join(f"<@{u}>" for u in selected)

            embed = discord.Embed(
                title="🎉 GIVEAWAY TERMINÉ 🎉",
                description=f"🎁 **Prix :** {gw['prize']}\n{result}",
                color=COLOR
            )

            await channel.send(embed=embed)
            self.data[gid]["ended"] = True
            save_data(self.data)

    @check_giveaways.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Giveaway(bot))
