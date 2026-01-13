import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
import time
import os


TOKEN = os.getenv("TOKEN")
REPORT_RECEIVER_IDS = [
    1424111016450592879,  
    1441741248451973241,   
    1444568142545162319    
]


intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)



@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Game(name="Buckingham Palace")
    )
    print("Status set to DND, activity: Playing Buckingham Palace")

# -------- Auto role and member --------
AUTO_ROLE_ID = 1448918566035263637
LOG_CHANNEL_ID = 1460757142972665998  # channel where the message is
LOG_MESSAGE_ID = 1460757287672217600  # the message the bot edits

@bot.event
async def on_member_join(member):
    # 1️⃣ Add auto role
    role = member.guild.get_role(AUTO_ROLE_ID)
    if role:
        await member.add_roles(role)
    
    # 2️⃣ Append join to log message
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel is None:
        return  # channel not found

    try:
        message = await channel.fetch_message(LOG_MESSAGE_ID)
    except discord.NotFound:
        return  # message not found

    # Generate Discord timestamp
    timestamp = int(time.time())
    new_entry = f"- {member.mention} | <t:{timestamp}>\n"

    # Append new entry to existing message
    updated_content = message.content + new_entry
    await message.edit(content=updated_content)
    
# -------- EMBED BUILDER --------
def mod_embed(guild, action, reason, moderator: discord.Member):
    role = moderator.top_role.name if moderator.top_role else "Staff"

    embed = discord.Embed(
        title=guild.name,
        description=f"You have been **{action}**!",
        color=discord.Color.red()
    )
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text=f"From {role}")
    return embed

# -------- BAN --------
@bot.tree.command(name="ban", description="Ban a member")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    embed = mod_embed(interaction.guild, "banned", reason, interaction.user)

    try:
        await member.send(embed=embed)
    except:
        pass

    await member.ban(reason=reason)
    await interaction.response.send_message(f"✅ {member} banned.", ephemeral=True)

# -------- KICK --------
@bot.tree.command(name="kick", description="Kick a member")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    embed = mod_embed(interaction.guild, "kicked", reason, interaction.user)

    try:
        await member.send(embed=embed)
    except:
        pass

    await member.kick(reason=reason)
    await interaction.response.send_message(f"✅ {member} kicked.", ephemeral=True)

# -------- TIMEOUT / MUTE --------
@bot.tree.command(name="timeout", description="Timeout (mute) a member")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(
    interaction: discord.Interaction,
    member: discord.Member,
    minutes: int,
    reason: str = "No reason provided"
):
    embed = mod_embed(interaction.guild, "timed out", reason, interaction.user)

    try:
        await member.send(embed=embed)
    except:
        pass

    await member.timeout(timedelta(minutes=minutes), reason=reason)
    await interaction.response.send_message(f"⏱️ {member} timed out.", ephemeral=True)

# -------- WARN --------
@bot.tree.command(name="warn", description="Warn a member")
@app_commands.checks.has_permissions(moderate_members=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    embed = mod_embed(interaction.guild, "warned", reason, interaction.user)

    try:
        await member.send(embed=embed)
    except:
        pass

    await interaction.response.send_message(f"⚠️ {member} warned.", ephemeral=True)

# -------- NOTICE --------
@bot.tree.command(name="notice", description="Send a notice to a member")
@app_commands.checks.has_permissions(moderate_members=True)
async def notice(interaction: discord.Interaction, member: discord.Member, message: str):
    embed = mod_embed(interaction.guild, "been sent a notice", message, interaction.user)

    try:
        await member.send(embed=embed)
    except:
        pass

    await interaction.response.send_message("✅ Notice sent.", ephemeral=True)

# -------- FILE REPORT --------
@bot.tree.command(name="report", description="File a report")
async def report(interaction: discord.Interaction, report_text: str):
    user = await bot.fetch_user(REPORT_RECEIVER_ID)
    await user.send(
        f"📝 **New Report**\n"
        f"From: {interaction.user} ({interaction.user.id})\n"
        f"Server: {interaction.guild}\n\n"
        f"{report_text}"
    )
    await interaction.response.send_message("✅ Report submitted.", ephemeral=True)

# -------- FILE LEAK --------
@bot.tree.command(name="leak", description="File a leak (link only)")
async def leak(interaction: discord.Interaction, link: str):
    user = await bot.fetch_user(REPORT_RECEIVER_ID)
    await user.send(
        f"🚨 **Leak Submitted**\n"
        f"From: {interaction.user} ({interaction.user.id})\n"
        f"Server: {interaction.guild}\n"
        f"Link: {link}"
    )
    await interaction.response.send_message("✅ Leak submitted.", ephemeral=True)

bot.run(TOKEN)
