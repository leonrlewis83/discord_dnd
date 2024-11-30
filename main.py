import logging
import traceback
import discord
import importlib
import inspect
from discord.ext import commands
from utils.DatabaseController import DatabaseController
from cogs.CharacterCreation import CharacterCreation
from config.ConfigLoader import ConfigLoader
from utils.LoggingHelper import Blacklist
from utils.Persona import ChatGPTPersona

# Configuring Logging
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler()]
)
for handler in logging.root.handlers:
    handler.addFilter(Blacklist('discord.client', 'discord.gateway'))

logger = logging.getLogger("bot.gateway")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)
sys_config = ConfigLoader()
db_config = sys_config.database
discord_config = sys_config.discord
openai_config =  sys_config.openai
db_controller = DatabaseController(
    db_host=db_config.DB_URL,
    db_port=db_config.DB_PORT,
    db_user=db_config.DB_USER,
    db_password=db_config.DB_PASSWORD,
    db_name=db_config.DB_DBNAME
)
extensions = [
    "cogs.Ysolde",
    "cogs.HelpAO",
    "cogs.CharacterCreation"
]

chatgpt_persona = ChatGPTPersona(persona="Ysolde is a Tiefling Apothecary who specializes in alchemy and healing.", api_key=openai_config.GPT_TOKEN)

SUCCESS_MESSAGE_TEMPLATE = "Successfully loaded extension: {}"

async def load_extensions():
    """
    Dynamically load extensions and pass only the required attributes.

    :param bot: The bot instance to pass to the methods.
    :param db_controller: The DatabaseController instance.
    :param chatgpt_persona: The ChatGPT persona instance.
    :param extensions: A list of extensions to load.
    """
    # Map available attributes
    available_attributes = {
        "bot": bot,
        "db_controller": db_controller,
        "chatgpt_persona": chatgpt_persona,
    }

    for extension in extensions:
        try:
            module = importlib.import_module(extension)
            attribute_name = extension.split(sep=".")[1]  # Extract the attribute name
            attribute = getattr(module, attribute_name)  # Import cog directly

            # Get the attribute's signature to determine required arguments
            signature = inspect.signature(attribute)
            required_args = [
                param.name
                for param in signature.parameters.values()
                if param.default == param.empty and param.kind in (param.POSITIONAL_OR_KEYWORD, param.POSITIONAL_ONLY)
            ]
            logger.debug(f"Inspection for {attribute_name}\nRequired Args:\n{required_args}")
            # Dynamically match required arguments to available attributes
            args_to_pass = [available_attributes[arg] for arg in required_args if arg in available_attributes]

            await bot.add_cog(attribute(*args_to_pass))  # Pass db_controller directly
            logger.info(f"Successfully loaded extension: {extension}")
        except Exception as exception:
            logger.error(f"Failed to load extension {extension}: {exception}")
            logger.error(traceback.format_exc())


@bot.event
async def on_ready():
    logger.info(f'Bot connected as {bot.user}')
    await load_extensions()



# Start Bot
bot.run(discord_config.SUPER_SECRET_TOKEN)
