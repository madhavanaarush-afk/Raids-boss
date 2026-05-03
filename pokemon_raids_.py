import discord
from discord.ext import commands
from discord import app_commands
import os

# 🔐 TOKEN (Railway ENV)
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True


# ================= BOT CLASS =================
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="?", intents=intents)

    async def setup_hook(self):
        # 🔄 Slash commands sync
        await self.tree.sync()


bot = MyBot()

# 👉 MAIN CHANNEL ID (optional, agar use karna ho)
MAIN_CHANNEL_ID = 1484694223578988564

watch_channels = set()


# ================= READY =================
@bot.event
async def on_ready():
    print(f"🔥 Logged in as {bot.user}")


# ================= ADD / REMOVE =================
@bot.command()
async def add(ctx, channel_id: int):
    watch_channels.add(channel_id)
    await ctx.send(f"✅ Added {channel_id}")


@bot.command()
async def remove(ctx, channel_id: int):
    watch_channels.discard(channel_id)
    await ctx.send(f"❌ Removed {channel_id}")


# ================= SLASH COMMAND (/raid) =================
@bot.tree.command(name="raid", description="Show raid meta list")
async def raid(interaction: discord.Interaction):

    text = """## Fire
★★★ **Reshiram** (hp/spatk) - z move (Blue Flare) | item: firium z
★★★ **Heatran** (hp/spatk) - z move (Eruption) | item: firium z
★☆☆ **Primal Groudon** (hp/spatk) - Move (Eruption)

## Psychic
★★★ **Mega Shadow Mewtwo Y** - Move: (Future Sight)
★★★ **Dawn Necrozma** (hp/spatk) - z move (Photon geyser) | item: ultranecrozium z
★☆☆ **Ultra Necrozma** (hp/spatk) - z move (Photon geyser) | item: ultranecrozium z

## Ghost
★★★ **Full Moon Lunala** (hp/spatk) - z move (Moongeist beam) | item: lunalium z
★★☆ **Dawn Necrozma** (hp/spatk) - z move (Moongeist beam) | item: lunalium z

## Steel
★★★ **Dusk Necrozma** (hp/atk) - z move (Sunsteel strike) | item: solganium z
★☆☆ **Jirachi** (hp/spatk) - z move (Doom desire) | item: steelium z
★☆☆ **Gigantamax Melmetal** (hp/atk) - move (G-max Meltdown)

## Fairy
★★★ **Magearna** (hp/spatk) - z move (Fleur cannon) | item: fairium z
★★☆ **Gigantamax Hatterene** (hp/spatk) - move (G-max smite)

## Flying
★★★ **Mega Rayquaza** (hp/spatk) - z move (Hurricane) | item: flyinium z
★★★ **Mega Rayquaza** (hp/atk) - z move (Dragon ascent) | item: flyinium z
★☆☆ **Ho-oh** (hp/atk) - z move (Sky attack) | item: flyinium z
★☆☆ **Shadow Lugia** (hp/spatk) - z move (Aeroblast) | item: flyinium z
★☆☆ **Gigantamax Corviknight** (hp/atk) - move (G-max wind rage)

## Poison
★★☆ **Eternatus** (hp/spatk) - z move (Sludge bomb) | item: poisonium z
★☆☆ **Muk** (hp/atk) - z move (Gunk shot) | item: poisonium z

Nature: (hp/atk) **Adamant** | (hp/spatk) **Modest**
★★★ Most Used
★★☆ Slightly Used / Good Substitute
★☆☆ Least Used
"""

    await interaction.response.send_message(text)


# ================= GLOBAL TEXT (NO PREFIX) =================
@bot.event
async def on_message(message):

    if message.content.lower() in ["global", "globals"]:
        embed = discord.Embed(
            title="🌸 Global Timing",
            color=0x2b2d31
        )

        embed.description = (
            "**No.  Start → End**\n\n"
            "➊  `4:00 PM  -  5:30 PM`\n"
            "➋  `7:00 PM  -  8:30 PM`\n"
            "➌  `10:00 PM - 11:30 PM`\n"
            "➍  `1:00 AM  -  2:30 AM`\n"
            "➎  `4:00 AM  -  5:30 AM`\n"
            "➏  `7:00 AM  -  8:30 AM`\n"
            "➐  `10:00 AM - 11:30 AM`\n"
            "➑  `1:00 PM  -  2:30 PM`"
        )

        await message.channel.send(embed=embed)
        return

    await bot.process_commands(message)


# ================= RUN =================
bot.run(TOKEN)