import discord
from discord.ext import commands
import asyncpg
import random

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

DATABASE_URL = "postgresql://username:password@localhost/dbname"


# Connect to PostgreSQL
async def create_db_pool():
    bot.db = await asyncpg.create_pool(DATABASE_URL)


@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")


# Step #1: Check for Empty Character Slot
@bot.command(name="newchar")
async def newchar(ctx):
    user_id = ctx.author.id
    # Check character slots in the database
    async with bot.db.acquire() as conn:
        char_count = await conn.fetchval(
            "SELECT COUNT(*) FROM characters WHERE user_id = $1", user_id
        )
        if char_count >= 3:  # Assume 3 max character slots
            await ctx.send("You do not have an available character slot to create a new character.")
            return

    # Proceed to step #2
    await ctx.send("Choose your stat generation method: (1) Standard Point Buy or (2) Rolling")
    msg = await bot.wait_for(
        "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
    )

    if msg.content == "1":
        await standard_point_buy(ctx, user_id)
    elif msg.content == "2":
        await rolling_method(ctx, user_id)
    else:
        await ctx.send("Invalid choice. Please start over by typing `!newchar`.")


# Step #3: Standard Point Buy
async def standard_point_buy(ctx, user_id):
    points = 27
    stats = {"Strength": 8, "Dexterity": 8, "Constitution": 8, "Intelligence": 8, "Wisdom": 8, "Charisma": 8}
    cost_table = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}

    def validate_points(stat, value):
        if value not in cost_table:
            return False
        new_total = points - (cost_table[value] - cost_table[stats[stat]])
        return new_total >= 0

    while points > 0:
        await ctx.send(f"Points remaining: {points}\nStats: {stats}")
        await ctx.send("Choose a stat to adjust (Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma):")
        stat_msg = await bot.wait_for(
            "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
        stat = stat_msg.content.capitalize()

        if stat not in stats:
            await ctx.send("Invalid stat. Try again.")
            continue

        await ctx.send(f"Current {stat}: {stats[stat]}. Enter new value (8-15):")
        value_msg = await bot.wait_for(
            "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
        try:
            value = int(value_msg.content)
        except ValueError:
            await ctx.send("Invalid number. Try again.")
            continue

        if validate_points(stat, value):
            points -= cost_table[value] - cost_table[stats[stat]]
            stats[stat] = value
        else:
            await ctx.send("Invalid choice. Not enough points or invalid range.")

    await ctx.send(f"Your final stats are: {stats}. Is this correct? (yes/no)")
    confirm_msg = await bot.wait_for(
        "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
    )

    if confirm_msg.content.lower() == "yes":
        await ctx.send("Stats confirmed! Moving to class selection.")
        await choose_class(ctx, user_id, stats)
    else:
        await ctx.send("Restarting point buy...")
        await standard_point_buy(ctx, user_id)


# Step #4: Rolling Method
async def rolling_method(ctx, user_id):
    def roll_3d6():
        return sum(random.randint(1, 6) for _ in range(3))

    def generate_grid():
        return [roll_3d6() for _ in range(9)]

    grid = generate_grid()
    while (
            sum(1 for x in grid if x < 6) >= 4
            or sum(1 for x in grid if x >= 15) < 2
            or sum(1 for x in grid if x == 18) >= 2
    ):
        grid = generate_grid()

    await ctx.send(f"Here is your grid: {grid}\nSelect a row, column, or diagonal (e.g., Row 1):")
    pool = []
    for _ in range(2):
        selection_msg = await bot.wait_for(
            "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
        selection = selection_msg.content.lower()

        if "row" in selection:
            row = int(selection.split()[-1]) - 1
            pool.extend(grid[row * 3: row * 3 + 3])
        elif "column" in selection:
            col = int(selection.split()[-1]) - 1
            pool.extend(grid[col::3])
        elif "diagonal" in selection:
            if "1" in selection:
                pool.extend([grid[0], grid[4], grid[8]])
            elif "2" in selection:
                pool.extend([grid[2], grid[4], grid[6]])
        else:
            await ctx.send("Invalid selection. Try again.")
            continue

    pool = list(set(pool))[:6]
    stats = {}
    for stat in ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]:
        await ctx.send(f"Choose a value for {stat} from your pool: {pool}")
        stat_msg = await bot.wait_for(
            "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
        value = int(stat_msg.content)
        if value in pool:
            stats[stat] = value
            pool.remove(value)
        else:
            await ctx.send("Invalid choice. Try again.")
            continue

    await ctx.send(f"Your final stats are: {stats}. Is this correct? (yes/no)")
    confirm_msg = await bot.wait_for(
        "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
    )

    if confirm_msg.content.lower() == "yes":
        await ctx.send("Stats confirmed! Moving to class selection.")
        await choose_class(ctx, user_id, stats)
    else:
        await ctx.send("Restarting rolling method...")
        await rolling_method(ctx, user_id)


# Step #5: Choose Class
async def choose_class(ctx, user_id, stats):
    classes = [
        "Barbarian", "Bard", "Cleric", "Druid", "Fighter",
        "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"
    ]
    await ctx.send(f"Choose a class from the following: {', '.join(classes)}")
    class_msg = await bot.wait_for(
        "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
    )
    chosen_class = class_msg.content.capitalize()

    if chosen_class in classes:
        await ctx.send(f"You selected {chosen_class}. Is this correct? (yes/no)")
        confirm_msg = await bot.wait_for(
            "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
        if confirm_msg.content.lower() == "yes":
            await ctx.send("Class confirmed! Moving to race selection.")
            await choose_race(ctx, user_id, stats, chosen_class)
        else:
            await ctx.send("Restarting class selection...")
            await choose_class(ctx, user_id, stats)
    else:
        await ctx.send("Invalid class. Try again.")
        await choose_class(ctx, user_id, stats)


# Step #6: Choose Race
async def choose_race(ctx, user_id, stats, chosen_class):
    races = [
        "Aasimar", "Dragonborn", "Dwarf", "Elf", "Gnome", "Goliath",
        "Halfling", "Human", "Orc", "Tiefling"
    ]
    await ctx.send(f"Choose a race from the following: {', '.join(races)}")
    race_msg = await bot.wait_for(
        "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
    )
    chosen_race = race_msg.content.capitalize()

    if chosen_race in races:
        await ctx.send(f"You selected {chosen_race}. Is this correct? (yes/no)")
        confirm_msg = await bot.wait_for(
            "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
        if confirm_msg.content.lower() == "yes":
            await finalize_character(ctx, user_id, stats, chosen_class, chosen_race)
        else:
            await ctx.send("Restarting race selection...")
            await choose_race(ctx, user_id, stats, chosen_class)
    else:
        await ctx.send("Invalid race. Try again.")
        await choose_race(ctx, user_id, stats, chosen_class)


# Step #7: Finalize Character
async def finalize_character(ctx, user_id, stats, chosen_class, chosen_race):
    async with bot.db.acquire() as conn:
        await conn.execute(
            "INSERT INTO characters (user_id, stats, class, race) VALUES ($1, $2, $3, $4)",
            user_id, stats, chosen_class, chosen_race
        )
    await ctx.send(f"Character creation complete! Stats: {stats}, Class: {chosen_class}, Race: {chosen_race}")


# Start Bot
bot.loop.run_until_complete(create_db_pool())
bot.run("YOUR_BOT_TOKEN")
