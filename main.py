import logging
import discord
from discord.ext import commands
from utils.DatabaseController import DatabaseController
from creation.CharacterSheet import CharacterCreation
from config.ConfigLoader import ConfigLoader
from utils.LoggingHelper import Blacklist

# Configuring Logging
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler()]
)
for handler in logging.root.handlers:
    handler.addFilter(Blacklist('discord.client', 'discord.gateway'))

bot_logger = logging.getLogger("bot.gateway")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
sys_config = ConfigLoader()
db_config = sys_config.database
discord_config = sys_config.discord
db_controller = DatabaseController(
    logging.getLogger("db"),
    db_url=db_config.DB_URL,
    db_port=db_config.DB_PORT,
    db_user=db_config.DB_USER,
    db_password=db_config.DB_PASSWORD,
    db_name=db_config.DB_DBNAME
)

character_creator = CharacterCreation(bot_logger, db_controller)

@bot.event
async def on_ready():
    bot_logger.info(f'Bot connected as {bot.user}')

# Step #1: Check for Empty Character Slot
@bot.command(name="newchar")
async def newchar(ctx):
    user_id = ctx.author.id
    char_count = db_controller.fetch_one("SELECT COUNT(*) AS count FROM characters WHERE user_id = %s", (user_id,))
    if char_count and char_count['count'] >= 3:  # Assume 3 max character slots
        await ctx.send("You do not have an available character slot to create a new character.")
        return

    # TODO: Refine this: Gross method of needing to pass bot object to newchar method
    await character_creator.newchar(ctx)

# Start Bot
bot.run(discord_config.SUPER_SECRET_TOKEN)
