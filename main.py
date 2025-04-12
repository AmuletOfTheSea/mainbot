import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from keep_alive import keep_alive
keep_alive()

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
        # Sync commands with Discord
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Helper function to check if the user has a specific role
def has_bot_perms_role(interaction: discord.Interaction):
    role_name = "Bot Perms"
    return any(role.name == role_name for role in interaction.user.roles)

# /completeorder command
@bot.tree.command(name="completeorder", description="Complete an order and send a private server link with an optional extra message.")
@app_commands.describe(
    user="User to ping",
    privateserver="The private server link",
    extramessage="Optional extra message to send"
)
async def completeorder(
    interaction: discord.Interaction, 
    user: discord.User, 
    privateserver: str, 
    extramessage: str = None
):
    if not has_bot_perms_role(interaction):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    # Prepare the final message
    final_message = f"Order completed for {user.mention}!\nPrivate Server Link: {privateserver}\n"  # Add private server link
    if extramessage:  # Add extra message if provided
        final_message += f"\nExtra Message: {extramessage}"

    # Send the message to the user via DM (private message)
    await user.send(final_message)
    await interaction.response.send_message(f"Order message sent to {user.mention} in DMs.", ephemeral=True)

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
async def addorder(
    interaction: discord.Interaction, 
    user: discord.User, 
    ordered_item: str, 
    price: str, 
    payment_method: str, 
    date: str, 
    extra_note: str = None
):
    if not has_bot_perms_role(interaction):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    # Create the order entry
    order_details = {
        "ordered_item": ordered_item,
        "price": price,
        "payment_method": payment_method,
        "date": date,
        "extra_note": extra_note
    }

    # Store the order in the orders dictionary
    if user.id not in orders:
        orders[user.id] = []
    orders[user.id].append(order_details)

    await interaction.response.send_message(f"Order added for {user.mention}.", ephemeral=True)

# /delorder command
@bot.tree.command(name="delorder", description="Delete an existing order for a user.")
@app_commands.describe(
    user="User to delete the order for",
    order_index="Order index to delete"
)
async def delorder(
    interaction: discord.Interaction, 
    user: discord.User, 
    order_index: int
):
    if not has_bot_perms_role(interaction):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    # Check if the user has orders
    if user.id not in orders or not orders[user.id]:
        await interaction.response.send_message(f"No orders found for {user.mention}.", ephemeral=True)
        return

    # Check if the order index is valid
    if order_index < 1 or order_index > len(orders[user.id]):
        await interaction.response.send_message("Invalid order index.", ephemeral=True)
        return

    # Delete the order
    orders[user.id].pop(order_index - 1)
    await interaction.response.send_message(f"Order {order_index} for {user.mention} has been deleted.", ephemeral=True)

# /orderlog command
@bot.tree.command(name="orderlog", description="View all orders for a user.")
@app_commands.describe(user="User to view the orders for")
async def orderlog(
    interaction: discord.Interaction, 
    user: discord.User
):
    if not has_bot_perms_role(interaction):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    # Check if the user has orders
    if user.id not in orders or not orders[user.id]:
        await interaction.response.send_message(f"No orders found for {user.mention}.", ephemeral=True)
        return

    # Display the orders
    order_list = "\n".join(
        [f"**Order {i+1}:** {order['ordered_item']}, Price: {order['price']}, Payment: {order['payment_method']}, Date: {order['date']}, Extra Note: {order['extra_note'] or 'N/A'}" 
         for i, order in enumerate(orders[user.id])]
    )
    await interaction.response.send_message(f"Orders for {user.mention}:\n{order_list}", ephemeral=True)

bot.run("MTM2MDcwOTAyOTQ5OTkwMDEyNw.G0S5Dm.eob1W7RCq4z0hJF80lqRtyN4hYudDdO0DW956k")
