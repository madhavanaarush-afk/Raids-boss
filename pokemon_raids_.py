import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

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


# ================= GLOBAL TIMING COMMAND =================
@bot.command()
async def globals(ctx):
    embed = discord.Embed(
        title="🌸 Global Timing",
        color=0x2b2d31
    )

    timings = (
        "**No.  Start → End**\n\n"
        "1.  `4:00 PM  -  5:30 PM`\n"
        "2.  `7:00 PM  -  8:30 PM`\n"
        "3.  `10:00 PM - 11:30 PM`\n"
        "4.  `1:00 AM  -  2:30 AM`\n"
        "5.  `4:00 AM  -  5:30 AM`\n"
        "6.  `7:00 AM  -  8:30 AM`\n"
        "7.  `10:00 AM - 11:30 AM`\n"
        "8.  `1:00 PM  -  2:30 PM`"
    )

    embed.description = timings

    await ctx.send(embed=embed)


# ================= JOIN BUTTON =================
class JoinView(discord.ui.View):
    def __init__(self, source_guild_id):
        super().__init__(timeout=None)
        self.source_guild_id = source_guild_id

    @discord.ui.button(label="🚀 Join Server", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = bot.get_guild(self.source_guild_id)

        if not guild:
            return await interaction.response.send_message("❌ Source server not found", ephemeral=True)

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


# ================= MESSAGE FORWARD =================
@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if not message.author.bot:
        return

    if message.channel.id not in watch_channels:
        return

    main = bot.get_channel(MAIN_CHANNEL_ID)
    if not main:
        return

    embed = discord.Embed(color=0x2b2d31)

    for e in message.embeds:
        if e.title:
            embed.title = e.title

        if e.description:
            embed.description = e.description

        for field in e.fields:
            embed.add_field(name=field.name, value=field.value, inline=field.inline)

        if e.image:
            embed.set_image(url=e.image.url)

    embed.set_footer(text=f"source:{message.guild.id}")

    view = JoinView(message.guild.id)

    await main.send(embed=embed, view=view)


# ================= RUN =================
bot.run(TOKEN)