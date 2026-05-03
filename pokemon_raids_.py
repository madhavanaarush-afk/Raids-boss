import discord
from discord.ext import commands
import os

# 🔐 TOKEN
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

# 👉 MAIN CHANNEL (forwarding ke liye)
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


# ================= RAID COMMAND =================
@bot.command()
async def raid(ctx):

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
*?tag raidmeta2 for page 2*
"""

    await ctx.send(text)


# ================= JOIN BUTTON =================
class JoinView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(label="🚀 Join Server", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = bot.get_guild(self.guild_id)

        if not guild:
            return await interaction.response.send_message("❌ Server not found", ephemeral=True)

        channel = None
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).create_instant_invite:
                channel = ch
                break

        if not channel:
            return await interaction.response.send_message("❌ No invite permission", ephemeral=True)

        invite = await channel.create_invite(max_age=300, max_uses=1)

        try:
            await interaction.user.send(invite.url)
            await interaction.response.send_message("📩 Check your DM!", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Enable DMs", ephemeral=True)


# ================= MESSAGE SYSTEM =================
@bot.event
async def on_message(message):

    # ❌ ignore self
    if message.author == bot.user:
        return

    # 🌸 GLOBAL (same channel)
    if message.content.lower() in ["global", "globals"]:
        embed = discord.Embed(title="🌸 Global Timing", color=0x2b2d31)

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

    # ================= FORWARD SYSTEM =================

    if not message.author.bot:
        return

    if message.channel.id not in watch_channels:
        return

    if message.channel.id == MAIN_CHANNEL_ID:
        return

    main = bot.get_channel(MAIN_CHANNEL_ID)
    if not main:
        return

    embed = discord.Embed(color=0x2b2d31)

    if message.content:
        embed.description = message.content

    for e in message.embeds:

        if e.title:
            embed.title = e.title

        if e.description:
            if embed.description:
                embed.description += "\n\n" + e.description
            else:
                embed.description = e.description

        for field in e.fields:
            embed.add_field(name=field.name, value=field.value, inline=field.inline)

        if e.url:
            embed.url = e.url

        if e.image and e.image.url:
            embed.set_image(url=e.image.url)

    if not embed.image:
        for att in message.attachments:
            if att.content_type and "image" in att.content_type:
                embed.set_image(url=att.url)

    embed.set_footer(text=f"source:{message.guild.id}")

    view = JoinView(message.guild.id)

    await main.send(embed=embed, view=view)


# ================= RUN =================
bot.run(TOKEN)