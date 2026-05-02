import discord
from discord.ext import commands
import os

# 🔐 TOKEN Railway se aayega
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

# 👉 apna main channel ID daal
MAIN_CHANNEL_ID = 1484694223578988564

# 👉 jaha se messages lena hai
watch_channels = set()


@bot.event
async def on_ready():
    print("🔥 BOT READY 🔥")
    print(f"Logged in as {bot.user}")


# ✅ test command
@bot.command()
async def ping(ctx):
    await ctx.send("pong 🏓")


# ✅ add channel
@bot.command()
async def add(ctx, channel_id: int):
    watch_channels.add(channel_id)
    await ctx.send(f"✅ Added {channel_id}")


@bot.event
async def on_message(message):
    await bot.process_commands(message)

    # ❌ ignore self
    if message.author == bot.user:
        return

    # ❌ sirf BOT messages allow
    if not message.author.bot:
        return

    # ❌ sirf selected channels
    if message.channel.id not in watch_channels:
        return

    # ❌ main channel loop avoid
    if message.channel.id == MAIN_CHANNEL_ID:
        return

    main = bot.get_channel(MAIN_CHANNEL_ID)
    if not main:
        return

    image_url = None
    final_url = None

    # 📸 attachments se image
    for att in message.attachments:
        if att.content_type and "image" in att.content_type:
            image_url = att.url

    # 💥 embeds se image + url
    for emb in message.embeds:
        if emb.image and emb.image.url:
            image_url = emb.image.url

        if emb.url:
            final_url = emb.url

    # ❌ agar image nahi mila to ignore
    if not image_url:
        return

    # 🔘 JOIN BUTTON
    view = discord.ui.View()
    view.add_item(
        discord.ui.Button(
            label="🚀 Join Channel",
            url=message.jump_url
        )
    )

    # 📤 FINAL CLEAN EMBED
    embed = discord.Embed(color=0x00ff88)

    embed.set_image(url=image_url)

    if final_url:
        embed.description = final_url

    await main.send(embed=embed, view=view)


# ❗ error show karega
@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"❌ Error: {error}")


bot.run(TOKEN)