import discord
from discord.ext import commands
import os

# 🔐 TOKEN
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="?", intents=intents)

# 👉 IDs CHANGE KARNA NA BHUL
MAIN_CHANNEL_ID = 1484694223578988564
SECOND_CHANNEL_ID = 1484837076741652530

watch_channels = set()

# 🧠 store messages
message_store = {}


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

        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).create_instant_invite:
                invite = await ch.create_invite(max_age=300, max_uses=1)
                try:
                    await interaction.user.send(invite.url)
                    return await interaction.response.send_message("📩 Check DM!", ephemeral=True)
                except:
                    return await interaction.response.send_message("❌ Enable DMs", ephemeral=True)

        await interaction.response.send_message("❌ No invite permission", ephemeral=True)


# ================= MESSAGE SYSTEM =================
@bot.event
async def on_message(message):

    # ❌ ignore own bot
    if message.author.id == bot.user.id:
        return

    await bot.process_commands(message)

    # ❌ sirf dusre bots
    if not message.author.bot:
        return

    # ❌ sirf selected channels
    if message.channel.id not in watch_channels:
        return

    # ❌ loop avoid
    if message.channel.id == MAIN_CHANNEL_ID:
        return

    # ❌ agar embed hi nahi hai to skip
    if not message.embeds:
        return

    main = bot.get_channel(MAIN_CHANNEL_ID)
    if not main:
        return

    original_embed = message.embeds[0]

    view = JoinView(message.guild.id)

    sent_msg = await main.send(embed=original_embed, view=view)

    # 🧠 store embed
    message_store[sent_msg.id] = {
        "embed": original_embed,
        "guild": message.guild.id
    }

    # ✅ auto react
    await sent_msg.add_reaction("✅")


# ================= REACTION SYSTEM =================
@bot.event
async def on_raw_reaction_add(payload):

    # ❌ sirf main channel
    if payload.channel_id != MAIN_CHANNEL_ID:
        return

    # ❌ sirf ✅
    if str(payload.emoji) != "✅":
        return

    # ❌ bot ignore
    if payload.user_id == bot.user.id:
        return

    # ❌ agar stored nahi hai
    if payload.message_id not in message_store:
        return

    data = message_store[payload.message_id]

    second = bot.get_channel(SECOND_CHANNEL_ID)
    if not second:
        return

    # 🚀 SAME EMBED FORWARD
    await second.send(embed=data["embed"], view=JoinView(data["guild"]))


# ================= RUN =================
bot.run(TOKEN)