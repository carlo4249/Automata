import os
import discord
from discord.ext import commands
from discord.ui import Button, View
from flask import Flask
from threading import Thread
import asyncio

# Bot setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Staff roles
STAFF_ROLES = [
    1409997551385706587,  # Overlord/owner
    1409998319572226228,  # Warlord/co-owner
    1409998422437658806,  # high-council
    1409998531200290876,  # Commander
    1409998743973007471   # Enforcer
]

# Application questions
APPLICATION_QUESTIONS = [
    "1. Roblox Username:",
    "2. Discord Username:",
    "3. Timezone:",
    "4. Age (optional if preferred private, but recommended):",
    "5. Why do you want to join the Automata Alliance?",
    "6. Do you have prior experience in other clans or factions? If so, which?",
    "7. Are you willing to attend trainings, deployments, and follow the chain of command?",
    "8. How active are you on Roblox/Discord weekly (estimate hours)?",
    "9. Who, if anyone, referred you to the Alliance?",
    "10. Do you agree to follow the Automata Alliance rules and Code of Conduct?"
]

# Response templates
ACCEPTANCE_TEMPLATE = """
**Application Accepted**

Welcome to the Automata Alliance, {username}! 

Your application has been reviewed and accepted by the command staff. You will now be granted the recruit role and given access to our training channels. Please check the server information channel for next steps.

*Discipline begins with truth.*
"""

DENIAL_TEMPLATE = """
**Application Denied**

Thank you for your interest in the Automata Alliance, {username}. 

After review by our command staff, we've decided not to move forward with your application at this time. This decision may be based on experience level, activity requirements, or other factors that don't align with our current needs.

You may reapply in 30 days if circumstances change.

*Discipline begins with truth.*
"""

# Keep-alive server
app = Flask('')

@app.route('/')
def home():
    return "Automata Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Bot events
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Applications"))

@bot.event
async def on_member_join(member):
    welcome_channel = bot.get_channel(1410001110844051456)
    if welcome_channel:
        embed = discord.Embed(
            title="Welcome to Automata Alliance!",
            description=f"Welcome {member.mention} to the Automata Alliance Discord server!\n\nPlease read the rules and check out the application process if you're interested in joining our clan.",
            color=0x3C3C3C
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1403687541634367559/1409997093753589800/a6a4ddd9-50dd-4699-8748-bc9842210888.jpg")
        embed.set_footer(text="Discipline begins with truth.")
        await welcome_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    # Close application tickets when a user leaves
    for channel in member.guild.channels:
        if isinstance(channel, discord.TextChannel) and (channel.name.startswith(f"apply-{member.name}") or channel.name.startswith(f"apply-{member.display_name}")):
            await channel.delete(reason="User left the server")

# Application system
class ApplicationView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Apply Now", style=discord.ButtonStyle.primary, custom_id="apply_button")
    async def apply_button(self, interaction: discord.Interaction, button: Button):
        # Check if user already has an application channel
        for channel in interaction.guild.channels:
            if isinstance(channel, discord.TextChannel) and (channel.name.startswith(f"apply-{interaction.user.name}") or channel.name.startswith(f"apply-{interaction.user.display_name}")):
                await interaction.response.send_message("You already have an open application ticket!", ephemeral=True)
                return
        
        # Create application channel
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
        }
        
        # Add staff roles to channel permissions
        for role_id in STAFF_ROLES:
            role = interaction.guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
        
        # Create channel
        channel_name = f"apply-{interaction.user.name}"[:100]  # Ensure channel name doesn't exceed limit
        category = discord.utils.get(interaction.guild.categories, name="Applications")
        
        try:
            channel = await interaction.guild.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                category=category,
                topic=f"Application ticket for {interaction.user}"
            )
        except discord.HTTPException as e:
            await interaction.response.send_message("Failed to create application channel. Please try again later.", ephemeral=True)
            return
        
        # Send application instructions
        embed = discord.Embed(
            title="Automata Alliance – Enlistment Application",
            description="Please copy and answer the following questions in this channel. Incomplete applications will be denied.",
            color=0x3C3C3C
        )
        embed.add_field(
            name="Application Questions",
            value="\n".join(APPLICATION_QUESTIONS),
            inline=False
        )
        embed.set_footer(text="Answer honestly. Discipline begins with truth.")
        
        await channel.send(f"{interaction.user.mention} {', '.join([f'<@&{role_id}>' for role_id in STAFF_ROLES])}")
        await channel.send(embed=embed)
        
        # Send response templates for staff
        staff_embed = discord.Embed(
            title="Staff Tools",
            description="Use the following templates to respond to applications:",
            color=0x3C3C3C
        )
        staff_embed.add_field(
            name="Acceptance Template",
            value=f"```{ACCEPTANCE_TEMPLATE}```",
            inline=False
        )
        staff_embed.add_field(
            name="Denial Template",
            value=f"```{DENIAL_TEMPLATE}```",
            inline=False
        )
        await channel.send(embed=staff_embed)
        
        await interaction.response.send_message(f"Your application channel has been created: {channel.mention}", ephemeral=True)

# Bot commands
@bot.command()
@commands.has_any_role(*STAFF_ROLES)
async def setup(ctx):
    """Setup the application system"""
    embed = discord.Embed(
        title="Automata Alliance – Enlistment Application",
        description="__**Instructions**__\nOpen a ticket to begin your enlistment process. Copy and answer the following questions inside your ticket. Incomplete applications will be denied.",
        color=0x3C3C3C
    )
    embed.add_field(
        name="Application Questions",
        value="\n".join(APPLICATION_QUESTIONS),
        inline=False
    )
    embed.add_field(
        name="Reminder",
        value="Failure to answer truthfully or meet basic standards may result in denial of entry.",
        inline=False
    )
    embed.set_footer(text="Answer honestly. Discipline begins with truth.")
    
    view = ApplicationView()
    await ctx.send(embed=embed, view=view)
    await ctx.message.delete()

@bot.command()
@commands.has_any_role(*STAFF_ROLES)
async def close(ctx):
    """Close the application ticket"""
    if ctx.channel.name.startswith("apply-"):
        await ctx.channel.delete()
    else:
        await ctx.send("This command can only be used in application channels.")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore unknown commands
    else:
        print(f"An error occurred: {error}")

# Run the bot
if __name__ == "__main__":
    # Check if we're in a build environment (no BOT_TOKEN)
    if not os.getenv("BOT_TOKEN"):
        print("Build environment detected - skipping bot execution")
    else:
        keep_alive()
        bot.run(os.environ['BOT_TOKEN'])
