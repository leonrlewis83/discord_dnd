import discord
from discord.ext import commands
import asyncpg
from creation.character import CharacterCreation

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# TODO: Abstract configurable properties to an external config json
DATABASE_URL = "postgresql://username:password@localhost/dbname"
SUPER_SECRET_TOKEN = "MY TOKEN"

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

    # TODO: Refine this: Gross method of needing to pass bot object to newchar method
    newuserchar = CharacterCreation()
    await newuserchar.newchar(bot, ctx)

# Start Bot
bot.loop.run_until_complete(create_db_pool())
bot.run(SUPER_SECRET_TOKEN)
