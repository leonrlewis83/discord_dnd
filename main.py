import discord
from discord.ext import commands
import psycopg2
from creation.character import CharacterCreation
from config.ConfigLoader import ConfigLoader

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
sys_config = ConfigLoader()
db_config = sys_config.database
discord_config = sys_config.discord

SUPER_SECRET_TOKEN = discord_config.SUPER_SECRET_TOKEN
DATABASE_CONFIG = {
    "dbname": db_config.DB_DBNAME,
    "user": db_config.DB_USER,
    "password": db_config.DB_PASSWORD,
    "host": db_config.DB_URL,
    "port": db_config.DB_PORT
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
