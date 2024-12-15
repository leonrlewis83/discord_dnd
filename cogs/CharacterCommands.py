import discord
from discord.ext import commands
from config.ConfigLoader import ConfigLoader
from utils.DatabaseController import DatabaseController


class CharacterDropdown(discord.ui.View):
    def __init__(self, character_data):
        super().__init__()
        self.character_data = character_data  # List of characters (dicts with character details)
        self.add_item(CharacterSelect(self.character_data))


class CharacterSelect(discord.ui.Select):
    def __init__(self, character_data):
        # Populate dropdown options with character names
        options = [
            discord.SelectOption(label=char["name"], description=f"View {char['name']} details.")
            for char in character_data
        ]
        super().__init__(placeholder="Choose your character...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Fetch the selected character details
        selected_name = self.values[0]
        character = next(
            (char for char in self.view.character_data if char["name"] == selected_name),
            None
        )
        if not character:
            await interaction.response.send_message("Character not found. Please try again.", ephemeral=True)
            return

        # Generate and send a Discord embed with character details
        embed = self.generate_character_embed(character)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @staticmethod
    def generate_character_embed(character):
        """
        Generate a Discord embed displaying character details.
        """
        embed = discord.Embed(
            title=f"{character['name']}'s Details",
            color=discord.Color.blue()
        )
        embed.add_field(name="Class", value=character['class'], inline=False)
        embed.add_field(name="Race", value=character['race'], inline=False)
        embed.add_field(name="Stats", value=character['stats'], inline=False)

        # Add an avatar if it exists
        if "avatar" in character and character["avatar"]:
            embed.set_thumbnail(url=character["avatar"])
        else:
            embed.set_thumbnail(url="https://via.placeholder.com/150")  # Default placeholder

        return embed


class CharacterCommands(commands.Cog):
    def __init__(self, bot, db_controller):
        self.bot = bot
        self.db_controller = db_controller

    @commands.command(name="pc")
    async def pc(self, ctx):
        """Show dropdown menu of characters associated with the user."""
        user_id = ctx.author.id

        try:
            # Query the database for characters
            characters = self.db_controller.fetch_all(
                "SELECT name, class, race, stats, avatar FROM characters WHERE user_id = %s", (user_id,)
            )

            if not characters:
                await ctx.send("You don't have any characters associated with your account.")
                return

            # Create a dropdown view with the retrieved characters
            view = CharacterDropdown(character_data=characters)
            await ctx.send("Select a character to view details:", view=view)

        except Exception as e:
            await ctx.send(f"An error occurred while fetching your characters: {e}")

    @commands.command(name="setavatar")
    async def setavatar(self, ctx, character_name: str, avatar_url: str):
        """
        Set or update a character's avatar.
        """
        user_id = ctx.author.id

        try:
            # Check if the character belongs to the user
            character = self.db_controller.fetch_one(
                "SELECT id FROM characters WHERE user_id = %s AND name = %s", (user_id, character_name)
            )
            if not character:
                await ctx.send(f"No character named '{character_name}' found for your account.")
                return

            # Update the avatar URL in the database
            self.db_controller.execute(
                "UPDATE characters SET avatar = %s WHERE id = %s", (avatar_url, character["id"])
            )
            await ctx.send(f"Avatar for '{character_name}' has been updated!")

        except Exception as e:
            await ctx.send(f"An error occurred while updating the avatar: {e}")


# Setup function to add the cog
async def setup(bot):
    """Setup function to load the CharacterCommands cog."""
    try:
        config = ConfigLoader()  # Instantiate ConfigLoader
        db_controller = DatabaseController(
            db_url=config.database.DB_URL,
            db_port=config.database.DB_PORT,
            db_user=config.database.DB_USER,
            db_password=config.database.DB_PASSWORD,
            db_name=config.database.DB_DBNAME
        )

        # Ensure the 'avatar' column exists in the 'characters' table
        ensure_avatar_column(db_controller)

        await bot.add_cog(CharacterCommands(bot, db_controller))
    except Exception as e:
        raise RuntimeError(f"Failed to initialize CharacterCommands cog: {e}")


def ensure_avatar_column(db_controller):
    """
    Check if the 'avatar' column exists in the 'characters' table. Add it if missing.
    """
    try:
        # Check if the 'avatar' column exists
        column_check_query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'characters' AND column_name = 'avatar';
        """
        result = db_controller.fetch_one(column_check_query)

        # If the 'avatar' column does not exist, add it
        if not result:
            add_column_query = """
                ALTER TABLE characters ADD COLUMN avatar VARCHAR(255) DEFAULT NULL;
            """
            db_controller.execute(add_column_query)
            print("Avatar column added to the characters table.")
        else:
            print("Avatar column already exists.")
    except Exception as e:
        raise RuntimeError(f"Error ensuring 'avatar' column in characters table: {e}")
