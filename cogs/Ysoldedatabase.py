from discord.ext import commands

class Ysolde(commands.Cog):
    def __init__(self, bot, db_controller):
        self.db_controller=db_controller
        self.bot=bot
        # Ysolde's inventory structure
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
    async def buy(self, ctx, item_name: str, quantity: int):
        """Allow players to buy items from Ysolde."""
        if item_name not in self.inventory:
            await ctx.send(f"Sorry, I don't have {item_name} for sale.")
            return

        item = self.inventory[item_name]

        if quantity > item["quantity"]:
            await ctx.send(f"Sorry, I only have {item['quantity']} of {item_name} available.")
            return

        total_cost = item["price"] * quantity
        self.inventory[item_name]["quantity"] -= quantity
        await ctx.send(f"You bought {quantity} {item_name}(s) for {total_cost} gold.")

        # Update database (if connected) about inventory transaction (purchase)
        try:
            cursor.execute(
                "INSERT INTO transactions (user_id, item_name, quantity, total_cost) VALUES (%s, %s, %s, %s)",
                (ctx.author.id, item_name, quantity, total_cost)
            )
            conn.commit()
        except Exception as e:
            print(f"Error updating database: {e}")
            await ctx.send("An error occurred while processing the transaction.")


    # Command for Ysolde to sell an item
    @commands.command(name="buy")
    async def sell(self, ctx, item_name: str, quantity: int):
        """Allow players to sell items to Ysolde."""
        if item_name not in self.inventory:
            await ctx.send(f"Sorry, I don't buy {item_name}.")
            return

        item = self.inventory[item_name]

        # Allow haggling - Ysolde pays slightly less than the normal price
        price_offered = item["price"] * 0.9  # Ysolde pays 90% of the normal price

        total_payment = price_offered * quantity
        self.inventory[item_name]["quantity"] += quantity
        await ctx.send(f"You sold {quantity} {item_name}(s) to me for {total_payment} gold.")

        # Update the database with the sale transaction (if connected)
        try:
            cursor.execute(
                "INSERT INTO transactions (user_id, item_name, quantity, total_cost) VALUES (%s, %s, %s, %s)",
                (ctx.author.id, item_name, -quantity, total_payment)
            )
            conn.commit()
        except Exception as e:
            print(f"Error updating database: {e}")
            await ctx.send("An error occurred while processing the transaction.")


    # Command to see recent transactions
    @commands.command(name="recent")
    async def transactions(self, ctx):
        """Show the most recent transactions."""
        try:
            cursor.execute("SELECT * FROM transactions WHERE user_id = %s ORDER BY transaction_time DESC LIMIT 5",
                           (ctx.author.id,))
            rows = cursor.fetchall()

            if not rows:
                await ctx.send("You have no recent transactions.")
                return

            transaction_list = "**Recent Transactions:**\n"
            for row in rows:
                transaction_list += f"{row[1]} | {row[2]} items | {row[3]} gold\n"  # item_name, quantity, total_cost
            await ctx.send(transaction_list)
        except Exception as e:
            print(f"Error retrieving transactions: {e}")
            await ctx.send("An error occurred while retrieving your transactions.")

def setup(bot, db_controller):
    bot.add_cog(Ysolde(bot, db_controller))
