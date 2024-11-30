from discord.ext import commands
from typing import Optional

from utils.Persona import ChatGPTPersona


class Ysolde(commands.Cog):
    def __init__(self, bot, db_controller, chatgpt_persona: ChatGPTPersona):
        self.db_controller = db_controller
        self.bot = bot
        self.chatgpt_persona = chatgpt_persona
        self.inventory = {
            "Healing Potion": {"price": 52.5, "description": "Restores 2d4+2 hit points.", "quantity": 10},
            "Antitoxin": {"price": 65, "description": "Cures poison effects on the user.", "quantity": 5},
            "Herbal Remedy": {"price": 39, "description": "Restores 1d4 hit points over 1 minute.", "quantity": 7},
            "Potion of Greater Healing": {"price": 130, "description": "Restores 4d4+4 hit points.", "quantity": 3},
            "Cure Wounds Scroll": {"price": 156, "description": "Scroll that allows casting of Cure Wounds.", "quantity": 2},
            "Alchemist's Fire": {"price": 65, "description": "A flammable substance that deals fire damage.", "quantity": 5},
            "Potion of Fire Resistance": {"price": 104, "description": "Grants resistance to fire for 1 hour.", "quantity": 4},
            "Herbalism Kit": {"price": 52.5, "description": "A kit to gather and create basic herbal remedies.", "quantity": 2},
            "Explorers Pack": {"price": 156, "description": "Contains rations, a bedroll, and other adventuring gear.",
                               "quantity": 1},
        }


    # Handle NPC inventory command
    @commands.command(name="Shop")
    async def inventory(self, ctx):
        """Displays Ysolde's inventory and prices."""
        inventory_list = "**Ysolde's Inventory**\n"
        for item, details in self.inventory.items():
            inventory_list += f"**{item}**: {details['price']} gold - {details['description']} (Available: {details['quantity']})\n"

        await ctx.send(inventory_list)


    # Command for Ysolde to buy an item
    @commands.command(name="sell")
    async def sell(self, ctx, item_name: str, quantity: int):
        """Allow players to sell items to Ysolde."""
        if item_name not in self.inventory:
            await ctx.send(f"Sorry, I don't buy {item_name}.")
            return

        item = self.inventory[item_name]

        # Ysolde offers 90% of the original price for the items
        price_offered = item["price"] * 0.9  # 90% of the price
        total_payment = price_offered * quantity
        self.inventory[item_name]["quantity"] += quantity

        await ctx.send(f"You sold {quantity} {item_name}(s) to Ysolde for {total_payment} gold.")

        # Update the database with the sale transaction
        try:
            self.db_controller.insert("transactions", {
                "user_id": ctx.author.id,
                "item_name": item_name,
                "quantity": -quantity,
                "total_cost": total_payment
            })
        except Exception as e:
            print(f"Error updating database: {e}")
            await ctx.send("An error occurred while processing the transaction.")


    # Command for Ysolde to sell an item
    # Command to buy an item from Ysolde
    @commands.command(name="buy")
    async def buy(self, ctx, item_name: str, quantity: int):
        """Allow players to buy items from Ysolde."""
        if item_name not in self.inventory:
            await ctx.send(f"Sorry, I don't have {item_name} for sale.")
            return

        item = self.inventory[item_name]

        # Check if Ysolde has enough stock
        if quantity > item["quantity"]:
            await ctx.send(f"Sorry, I only have {item['quantity']} of {item_name} available.")
            return

        # Calculate total cost
        total_cost = item["price"] * quantity

        # Assume the player has a method to retrieve their gold balance
        player_gold = 1000  # You should fetch the actual player's gold from the database

        # Check if the player has enough gold
        if player_gold < total_cost:
            await ctx.send(f"You don't have enough gold to buy {quantity} {item_name}(s). You need {total_cost} gold.")
            return

        # Deduct gold from the player's account (assumes you have a gold column in your database)
        try:
            self.db_controller.update("players", {"gold": player_gold - total_cost}, "user_id = %s", (ctx.author.id,))
        except Exception as e:
            await ctx.send(f"An error occurred while processing the transaction: {e}")
            return

        # Update Ysolde's inventory
        self.inventory[item_name]["quantity"] -= quantity
        await ctx.send(f"You bought {quantity} {item_name}(s) for {total_cost} gold.")

        # Log the transaction in the database
        try:
            self.db_controller.insert("transactions", {
                "user_id": ctx.author.id,
                "item_name": item_name,
                "quantity": quantity,
                "total_cost": total_cost
            })
        except Exception as e:
            print(f"Error updating database: {e}")
            await ctx.send("An error occurred while processing the transaction.")


    # Command to see recent transactions
    @commands.command(name="transactions")
    async def transactions(self, ctx):
        """Show the most recent transactions."""
        try:
            rows = self.db_controller.fetch_all(
                "SELECT * FROM transactions WHERE user_id = %s ORDER BY transaction_time DESC LIMIT 5",
                (ctx.author.id,)
            )

            if not rows:
                await ctx.send("You have no recent transactions.")
                return

            transaction_list = "**Recent Transactions:**\n"
            for row in rows:
                transaction_list += f"{row['item_name']} | {row['quantity']} items | {row['total_cost']} gold\n"
            await ctx.send(transaction_list)

        except Exception as e:
            print(f"Error retrieving transactions: {e}")
            await ctx.send("An error occurred while retrieving your transactions.")
