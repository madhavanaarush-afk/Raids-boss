import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

# 👉 MAIN CHANNEL (yahan sab send hoga)
MAIN_CHANNEL_ID = 1484694223578988564

watch_channels = set()


# ================= READY =================
@bot.event
async def on_ready():
    print("🔥 BOT READY 🔥")
    print(bot.user)


# ================= BUTTON VIEW =================
class JoinView(discord.ui.View):
    def __init__(self, source_guild_id: int):
        super().__init__(timeout=None)
        self.source_guild_id = source_guild_id  # 👈 ORIGINAL SERVER STORE

    @discord.ui.button(
        label="🚀 Join Server",
        style=discord.ButtonStyle.green,
        custom_id="join_button"
    )
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = bot.get_guild(self.source_guild_id)

        if not guild:
            await interaction.response.send_message("❌ Source server not found", ephemeral=True)
            return

        # find channel with invite permission
        channel = None
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).create_instant_invite:
                channel = ch
                break

        if not channel:
            await interaction.response.send_message("❌ No invite permission in source server", ephemeral=True)
            return

        try:
            invite = await channel.create_invite(
                max_age=300,
                max_uses=1,
                unique=True
            )

            await interaction.user.send(
                f"👋 This is the server where the content came from:\n{invite.url}"
            )

            await interaction.response.send_message("📩 Check your DM!", ephemeral=True)

        except discord.Forbidden:
            await interaction.response.send_message("❌ Enable DMs first", ephemeral=True)


# ================= WATCH SYSTEM =================
@bot.command()
async def add(ctx, channel_id: int):
    watch_channels.add(channel_id)
    await ctx.send(f"✅ Watching {channel_id}")


# ================= MESSAGE FORWARD =================
@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author == bot.user:
        return

    if not message.author.bot:
        return

    if message.channel.id not in watch_channels:
        return

    main_channel = bot.get_channel(MAIN_CHANNEL_ID)
    if not main_channel:
        return

    image_url = None
    final_url = None

    # 📸 image detect
    for att in message.attachments:
        if att.content_type and "image" in att.content_type:
            image_url = att.url

    for emb in message.embeds:
        if emb.image and emb.image.url:
            image_url = emb.image.url

        if emb.url:
            final_url = emb.url

    if not image_url:
        return

    # 🔘 IMPORTANT: pass ORIGINAL SERVER ID here
    view = JoinView(message.guild.id)

    embed = discord.Embed(color=0x00ff88)
    embed.set_image(url=image_url)

    if final_url:
        embed.description = final_url

    await main_channel.send(embed=embed, view=view)


# ================= RUN =================
bot.run(TOKEN)