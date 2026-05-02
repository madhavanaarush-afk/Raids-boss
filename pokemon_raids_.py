import discord
from discord.ext import commands
import re
import os

# 🔐 TOKEN Railway se aayega
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

MAIN_CHANNEL_ID = 1484694223578988564
watch_channels = set()

url_pattern = re.compile(r"(https?://\S+)")

@bot.event
async def on_ready():
    print("🔥 BOT READY 🔥")
    print(f"Logged in as {bot.user}")

# ✅ ping command (test)
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

    # ❌ avoid loop
    if message.channel.id == MAIN_CHANNEL_ID:
        return

    # ❌ only selected channels
    if message.channel.id not in watch_channels:
        return

    main = bot.get_channel(MAIN_CHANNEL_ID)
    if not main:
        print("Main channel not found")
        return

    urls = []
    images = []

    # 🔗 TEXT URL
    if message.content:
        urls += url_pattern.findall(message.content)

    # 📸 ATTACHMENTS
    for att in message.attachments:
        if att.content_type and "image" in att.content_type:
            images.append(att.url)

    # 💥 EMBEDS
    embeds_to_send = []

    for emb in message.embeds:
        print("Embed detected")

        new_embed = discord.Embed(
            title=emb.title,
            description=emb.description,
            color=0x00ff88,
            timestamp=message.created_at
        )

        if emb.image and emb.image.url:
            images.append(emb.image.url)
            new_embed.set_image(url=emb.image.url)

        if emb.thumbnail and emb.thumbnail.url:
            new_embed.set_thumbnail(url=emb.thumbnail.url)

        if emb.description:
            urls += url_pattern.findall(emb.description)

        if emb.url:
            urls.append(emb.url)

        embeds_to_send.append(new_embed)

    if not embeds_to_send and not urls and not images and not message.content:
        print("Nothing detected")
        return

    # 🔘 JOIN BUTTON
    view = discord.ui.View()
    view.add_item(
        discord.ui.Button(
            label="🚀 Join Channel",
            url=message.jump_url
        )
    )

    # 📤 SEND
    if embeds_to_send:
        for e in embeds_to_send:
            await main.send(embed=e, view=view)
    else:
        embed = discord.Embed(
            description=message.content if message.content else "No text",
            color=0x00ff88,
            timestamp=message.created_at
        )

        if images:
            embed.set_image(url=images[0])

        if urls:
            embed.add_field(name="🔗 Links", value="\n".join(urls), inline=False)

        await main.send(embed=embed, view=view)

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"❌ Error: {error}")

bot.run(TOKEN)