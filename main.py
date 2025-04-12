import os
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

# For GitHub secret
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Order storage (in memory)
orders = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Helper function to check if the user has a specific role
def has_bot_perms_role(interaction: discord.Interaction):
    role_name = "Bot Perms"
    member = interaction.guild.get_member(interaction.user.id)
    if member is None:
        return False
    return any(role.name == role_name for role in member.roles)

# /completeorder command
@bot.tree.command(name="completeorder", description="Complete an order and send a private server link with an optional extra message.")
@app_commands.describe(
    user="User to ping",
    privateserver="The private server link",
    extramessage="Optional extra message to send"
)
async def completeorder(interaction: discord.Interaction, user: discord.User, privateserver: str, extramessage: str = None):
    if not has_bot_perms_role(interaction):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    final_message = f"Order completed for {user.mention}!\nPrivate Server Link: {privateserver}"
    if extramessage:
        final_message += f"\nExtra Message: {extramessage}"

    try:
        await user.send(final_message)
        await interaction.response.send_message(f"Order message sent to {user.mention} in DMs.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"Could not send DM to {user.mention}.", ephemeral=True)

# /addorder command
@bot.tree.command(name="addorder", description="Add a new order for a user.")
@app_commands.describe(
    user="User to ping",
    ordered_item="What the user ordered",
    price="Price of the order",
    payment_method="Payment method used",
    date="Date of the order",
    extra_note="Extra note for the order"
)
async def addorder(interaction: discord.Interaction, user: discord.User, ordered_item: str, price: str, payment_method: str, date: str, extra_note: str = None):
    if not has_bot_perms_role(interaction):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    order_details = {
        "ordered_item": ordered_item,
        "price": price,
        "payment_method": payment_method,
        "date": date,
        "extra_note": extra_note
    }

    if user.id not in orders:
        orders[user.id] = []
    orders[user.id].append(order_details)

    await interaction.response.send_message(f"Order added for {user.mention}.", ephemeral=True)

# /delorder command
@bot.tree.command(name="delorder", description="Delete an existing order for a user.")
@app_commands.describe(user="User to delete the order for", order_index="Order index to delete")
async def delorder(interaction: discord.Interaction, user: discord.User, order_index: int):
    if not has_bot_perms_role(interaction):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    if user.id not in orders or not orders[user.id]:
        await interaction.response.send_message(f"No orders found for {user.mention}.", ephemeral=True)
        return

    if order_index < 1 or order_index > len(orders[user.id]):
        await interaction.response.send_message("Invalid order index.", ephemeral=True)
        return

    orders[user.id].pop(order_index - 1)
    await interaction.response.send_message(f"Order {order_index} for {user.mention} has been deleted.", ephemeral=True)

# /orderlog command
@bot.tree.command(name="orderlog", description="View all orders for a user.")
@app_commands.describe(user="User to view the orders for")
async def orderlog(interaction: discord.Interaction, user: discord.User):
    if not has_bot_perms_role(interaction):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    if user.id not in orders or not orders[user.id]:
        await interaction.response.send_message(f"No orders found for {user.mention}.", ephemeral=True)
        return

    order_list = "\n".join(
        [f"**Order {i+1}:** {order['ordered_item']}, Price: {order['price']}, Payment: {order['payment_method']}, Date: {order['date']}, Extra Note: {order['extra_note'] or 'N/A'}"
         for i, order in enumerate(orders[user.id])]
    )
    await interaction.response.send_message(f"Orders for {user.mention}:\n{order_list}", ephemeral=True)

# Run the bot using the secret
bot_token = os.getenv("DISCORD_BOT_TOKEN")
if not bot_token:
    raise ValueError("DISCORD_BOT_TOKEN not set in environment.")
bot.run(bot_token)
