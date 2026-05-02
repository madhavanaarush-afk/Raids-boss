import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

MAIN_CHANNEL_ID = 1484694223578988564
watch_channels = set()


@bot.event
async def on_ready():
    print("🔥 BOT READY 🔥")


# ================= BUTTON =================
class JoinView(discord.ui.View):
    def __init__(self, source_guild_id: int):
        super().__init__(timeout=None)
        self.source_guild_id = source_guild_id

    @discord.ui.button(label="🚀 Join Server", style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = bot.get_guild(self.source_guild_id)

        if not guild:
            await interaction.response.send_message("❌ Source server not found", ephemeral=True)
            return

        channel = None
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).create_instant_invite:
                channel = ch
                break

        if not channel:
            await interaction.response.send_message("❌ No invite permission", ephemeral=True)
            return

        invite = await channel.create_invite(
            max_age=300,
            max_uses=1,
            unique=True
        )

        try:
            await interaction.user.send(f"👋 Invite from source server:\n{invite.url}")
            await interaction.response.send_message("📩 Check DM!", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Enable DMs", ephemeral=True)


# ================= ADD CHANNEL =================
@bot.command()
async def add(ctx, channel_id: int):
    watch_channels.add(channel_id)
    await ctx.send("✅ Added")


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

    main = bot.get_channel(MAIN_CHANNEL_ID)
    if not main:
        return

    image_url = None
    final_url = None

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

    # 🔥 IMPORTANT FIX: store source guild ID in footer
    embed = discord.Embed(color=0x00ff88)
    embed.set_image(url=image_url)

    if final_url:
        embed.description = final_url

    embed.set_footer(text=f"source:{message.guild.id}")

    view = JoinView(message.guild.id)

    await main.send(embed=embed, view=view)


bot.run(TOKEN)