import discord
from discord.ext import commands
import os

# 🔐 Railway ENV TOKEN
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix="?", intents=intents)

MAIN_CHANNEL_ID = 1484694223578988564
FINAL_CHANNEL_ID = 123456789012345678

watch_channels = set()


# ================= READY =================
@bot.event
async def on_ready():
    print(f"🔥 Logged in as {bot.user}")


# ================= ADD =================
@bot.command()
async def add(ctx, channel_id: int):
    watch_channels.add(channel_id)
    await ctx.send(f"✅ Added {channel_id}")


# ================= ADD MULTI =================
@bot.command()
async def addmulti(ctx, *channel_ids):
    added = 0
    for cid in channel_ids:
        try:
            cid = int(cid)
            watch_channels.add(cid)
            added += 1
        except:
            pass
    await ctx.send(f"✅ Added {added} channels")


# ================= REMOVE =================
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

    if message.author.id == bot.user.id:
        return

    if message.channel.id in [MAIN_CHANNEL_ID, FINAL_CHANNEL_ID]:
        return

    if not message.author.bot:
        await bot.process_commands(message)
        return

    if message.channel.id not in watch_channels:
        return

    if message.embeds:
        for e in message.embeds:
            if e.footer and "forwarded-by-bot" in e.footer.text:
                return

    if not message.embeds and not message.attachments:
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

        if e.image and e.image.url:
            embed.set_image(url=e.image.url)

        if e.thumbnail and e.thumbnail.url:
            embed.set_thumbnail(url=e.thumbnail.url)

    if not embed.image:
        for att in message.attachments:
            if att.content_type and "image" in att.content_type:
                embed.set_image(url=att.url)

    embed.set_footer(text="forwarded-by-bot")

    sent = await main.send(embed=embed, view=JoinView(message.guild.id))

    await sent.add_reaction("✅")


# ================= REACTION SYSTEM =================
@bot.event
async def on_reaction_add(reaction, user):

    if user.bot:
        return

    if reaction.message.channel.id != MAIN_CHANNEL_ID:
        return

    if str(reaction.emoji) != "✅":
        return

    final = bot.get_channel(FINAL_CHANNEL_ID)
    if not final:
        return

    msg = reaction.message
    embed = msg.embeds[0] if msg.embeds else None

    await final.send(embed=embed, view=JoinView(msg.guild.id))


# ================= RUN =================
bot.run(TOKEN)