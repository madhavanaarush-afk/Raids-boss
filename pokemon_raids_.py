import discord
from discord.ext import commands
import os

# 🔐 TOKEN (Railway / env)
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

# 👉 MAIN CHANNEL (jahan invite banega)
MAIN_CHANNEL_ID = 1484694223578988564

# 👉 watched channels
watch_channels = set()


# ================= READY =================
@bot.event
async def on_ready():
    print("🔥 BOT READY 🔥")
    print(f"Logged in as {bot.user}")


# ================= TEST =================
@bot.command()
async def ping(ctx):
    await ctx.send("pong 🏓")


# ================= ADD CHANNEL =================
@bot.command()
async def add(ctx, channel_id: int):
    watch_channels.add(channel_id)
    await ctx.send(f"✅ Added {channel_id}")


# ================= JOIN BUTTON SYSTEM =================
class JoinView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🚀 Join Server",
        style=discord.ButtonStyle.green,
        custom_id="join_button"
    )
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        channel = bot.get_channel(MAIN_CHANNEL_ID)

        if not channel:
            await interaction.response.send_message("❌ Main channel not found", ephemeral=True)
            return

        try:
            invite = await channel.create_invite(
                max_age=300,
                max_uses=1,
                unique=True
            )

            await interaction.user.send(
                f"👋 Here is your server invite link:\n{invite.url}"
            )

            await interaction.response.send_message(
                "📩 Check your DM!",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Enable DMs to receive invite.",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {e}",
                ephemeral=True
            )


# ================= MESSAGE HANDLER =================
@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author == bot.user:
        return

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

    # 📸 image from attachments
    for att in message.attachments:
        if att.content_type and "image" in att.content_type:
            image_url = att.url

    # 📸 image from embeds
    for emb in message.embeds:
        if emb.image and emb.image.url:
            image_url = emb.image.url

        if emb.url:
            final_url = emb.url

    if not image_url:
        return

    # 🔘 BUTTON VIEW
    view = JoinView()

    embed = discord.Embed(color=0x00ff88)
    embed.set_image(url=image_url)

    if final_url:
        embed.description = final_url

    await main.send(embed=embed, view=view)


# ================= ERROR HANDLER =================
@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"❌ Error: {error}")


bot.run(TOKEN)