import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="?", intents=intents)

# 👉 CHANNEL IDs
MAIN_CHANNEL_ID = 1484694223578988564
SECOND_CHANNEL_ID = 1484837076741652530  # 🔁 change this
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
            await interaction.response.send_message("📩 Check DM!", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Enable DMs", ephemeral=True)


# ================= MESSAGE SYSTEM =================
@bot.event
async def on_message(message):

    if message.author.id == bot.user.id:
        return

    await bot.process_commands(message)

    # ❌ sirf dusre bots
    if not message.author.bot:
        return

    if message.channel.id not in watch_channels:
        return

    if message.channel.id == MAIN_CHANNEL_ID:
        return

    main = bot.get_channel(MAIN_CHANNEL_ID)
    if not main:
        return

    image_url = None
    final_url = None
    text_data = ""

    # 📸 attachments
    for att in message.attachments:
        if att.content_type and "image" in att.content_type:
            image_url = att.url

    # 💥 embeds
    for e in message.embeds:
        if e.image and e.image.url:
            image_url = e.image.url

        if e.url:
            final_url = e.url

        if e.title:
            text_data += f"**{e.title}**\n"

        if e.description:
            text_data += f"{e.description}\n\n"

        for field in e.fields:
            text_data += f"**{field.name}**\n{field.value}\n\n"

    if not image_url:
        return

    embed = discord.Embed(color=0x2b2d31)
    embed.set_image(url=image_url)

    if final_url:
        embed.description = f"{final_url}\n\n{text_data}"

    view = JoinView(message.guild.id)

    sent_msg = await main.send(embed=embed, view=view)

    # ✅ auto react
    await sent_msg.add_reaction("✅")


# ================= REACTION SYSTEM =================
@bot.event
async def on_raw_reaction_add(payload):

    if payload.channel_id != MAIN_CHANNEL_ID:
        return

    if str(payload.emoji) != "✅":
        return

    if payload.user_id == bot.user.id:
        return

    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)

    user = await bot.fetch_user(payload.user_id)
    if user.bot:
        return

    second = bot.get_channel(SECOND_CHANNEL_ID)
    if not second:
        return

    # 🚀 forward approved message
    if message.embeds:
        await second.send(embed=message.embeds[0], view=JoinView(message.guild.id))


# ================= RUN =================
bot.run(TOKEN)