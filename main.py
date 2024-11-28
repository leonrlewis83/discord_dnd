import discord
from discord.ext import commands
import psycopg2
from creation.character import CharacterCreation

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# TODO: Abstract configurable properties to an external config json
SUPER_SECRET_TOKEN = ""
DATABASE_CONFIG = {
}

#  Helper function to connect to the database
def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

# Step #1: Check for Empty Character Slot
@bot.command(name="newchar")
async def newchar(ctx):
    user_id = ctx.author.id
    with get_db_connection() as conn:
        # Check character slots in the database
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM characters WHERE user_id = %s", (user_id, )
            )
            char_count = cur.fetchone()[0]
            if char_count >= 3:  # Assume 3 max character slots
                await ctx.send("You do not have an available character slot to create a new character.")
                return

    # TODO: Refine this: Gross method of needing to pass bot object to newchar method
    newuserchar = CharacterCreation()
    await newuserchar.newchar(bot, ctx)

# Start Bot
bot.run(SUPER_SECRET_TOKEN)
