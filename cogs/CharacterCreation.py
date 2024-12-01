import logging
import json
import traceback
from discord.ext import commands
from models.Character import Character
from entities.Classes import ClassEnum
from entities.Races import RacesEnum
from entities.Stats import StatsEnum
from utils.Mathhelpers import generate_grid

# Set up logging
logger = logging.getLogger("bot.character")


class CharacterCreation(commands.Cog):
    def __init__(self, bot, db_controller):
        self.db_controller = db_controller
        self.bot = bot
        self.user_id = None
        self.character = None

    # Step #1: Check for Empty Character Slot
    @commands.command(name="newchar")
    async def newchar(self, ctx):
        self.user_id = ctx.author.id
        self.character = Character(self.user_id)
        char_count = self.db_controller.fetch_one("SELECT COUNT(*) AS count FROM characters WHERE user_id = :user_id",
                                             {"user_id": self.user_id})
        if char_count and char_count['count'] >= 3:  # Assume 3 max character slots
            await ctx.send("You do not have an available character slot to create a new character.")
            return

        # Step #1: Get temporary character name
        await ctx.send("Please provide a temporary name for your character (you can change it later):")
        name_msg = await ctx.bot.wait_for(
            "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
        self.character.name = name_msg.content
        await ctx.send(f"Your temporary character name is {self.character.name}. You can change it later.")
        self.db_controller.insert(self.character)

        # Proceed to step #2
        await ctx.send("Choose your stat generation method: (1) Standard Point Buy or (2) Rolling")
        msg = await ctx.bot.wait_for(
            "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )

        if msg.content == "1":
            await self.standard_point_buy(ctx)
        elif msg.content == "2":
            await self.rolling_method(ctx)
        else:
            await ctx.send("Invalid choice. Please start over by typing `!newchar`.")

    # Step #3: Standard Point Buy
    async def standard_point_buy(self, ctx):
        """
        Guide the user through the Standard Point Buy system for assigning stats.

        :param ctx: Discord context for sending and receiving messages.
        """
        points = 27
        stats = {stat: 8 for stat in StatsEnum}  # Initialize all stats to 8
        cost_table = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}

        def validate_points(assigning_stat: StatsEnum, assigning_value: int) -> bool:
            """
            Validate whether the new stat value can be assigned given the available points.
            """
            if assigning_value not in cost_table:
                return False
            new_total = points - (cost_table[assigning_value] - cost_table[stats[assigning_stat]])
            return new_total >= 0

        while points > 0:
            await ctx.send(
                f"Points remaining: {points}\nStats: {', '.join(f'{stat.display_name}: {value}' for stat, value in stats.items())}"
            )
            await ctx.send(
                "Choose a stat to adjust (Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma):")

            # Get the user's stat selection
            stat_msg = await ctx.bot.wait_for(
                "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
            stat = next((s for s in StatsEnum if s.display_name.lower() == stat_msg.content.lower()), None)

            if not stat:
                await ctx.send("Invalid stat. Try again.")
                continue

            await ctx.send(f"Current {stat.display_name}: {stats[stat]}. Enter new value (8-15):")

            # Get the user's desired value for the selected stat
            value_msg = await ctx.bot.wait_for(
                "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
            try:
                value = int(value_msg.content)
            except ValueError:
                await ctx.send("Invalid number. Try again.")
                continue

            # Validate and assign the value
            if validate_points(stat, value):
                points -= cost_table[value] - cost_table[stats[stat]]
                stats[stat] = value
            else:
                await ctx.send("Invalid choice. Not enough points or invalid range.")

        # Final confirmation
        await ctx.send(
            f"Your final stats are: {', '.join(f'{stat.display_name}: {value}' for stat, value in stats.items())}. Is this correct? (yes/no)")
        confirm_msg = await ctx.bot.wait_for(
            "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )

        if confirm_msg.content.lower() == "yes":
            self.character.stats = stats
            await ctx.send(f"Stats confirmed!\n\nMoving to class selection...")
            await self.choose_class(ctx)
            # Save stats here
            await self.save_character_grid(ctx, stats)
        else:
            await ctx.send("Restarting point buy...")
            await self.standard_point_buy(ctx)

    async def save_character_grid(self, ctx, stats):
        """Save the current stats or grid after confirmation."""
        await ctx.send(f"Saving your current stats and grid...\n{stats}")
        # db_data = {
        #     "user_id": self.character.user_id,
        #     "name": self.character.name,
        #     "stats": json.dumps(stats)
        # }
        self.db_controller.update(self.character)

    # Step #4: Rolling Method
    async def rolling_method(self, ctx):
        grid = generate_grid()

        while (
                sum(1 for x in grid if x < 6) >= 4
                or sum(1 for x in grid if x >= 15) < 2
                or sum(1 for x in grid if x == 18) >= 2
        ):
            grid = generate_grid()

        await ctx.send(f"Here is your grid:\n{grid[:3]}\n{grid[3:6]}\n{grid[6:9]}")
        pool = []
        selected_choices = []

        for _ in range(2):  # Prompt user for 2 valid grid selections
            while True:  # Only accept valid selections
                await ctx.send("Select a row, column, or diagonal (e.g., Row 1, Col 1, or Diag 1):")
                selection_msg = await ctx.bot.wait_for(
                    "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
                )
                selection = selection_msg.content.lower()

                # Validate and process the selection
                if "row" in selection or "r" in selection:
                    row = int(selection.split()[-1]) - 1
                    if (row, "row") not in selected_choices:
                        pool.extend(grid[row * 3: row * 3 + 3])
                        selected_choices.append((row, "row"))
                        break  # Valid selection, exit the loop
                    else:
                        await ctx.send("You've already selected this row. Try again.")
                        continue  # Invalid selection, prompt again
                elif "column" in selection or "col" in selection:
                    col = int(selection.split()[-1]) - 1
                    if (col, "col") not in selected_choices:
                        pool.extend(grid[col::3])
                        selected_choices.append((col, "col"))
                        break  # Valid selection, exit the loop
                    else:
                        await ctx.send("You've already selected this column. Try again.")
                        continue  # Invalid selection, prompt again
                elif "diagonal" in selection or "diag" in selection:
                    if "1" in selection and (0, "diag") not in selected_choices:
                        pool.extend([grid[0], grid[4], grid[8]])
                        selected_choices.append((0, "diag"))
                        break  # Valid selection, exit the loop
                    elif "2" in selection and (1, "diag") not in selected_choices:
                        pool.extend([grid[2], grid[4], grid[6]])
                        selected_choices.append((1, "diag"))
                        break  # Valid selection, exit the loop
                    else:
                        await ctx.send("You've already selected this diagonal. Try again.")
                        continue  # Invalid selection, prompt again
                else:
                    await ctx.send("Invalid selection. Try again.")
                    continue  # Invalid selection, prompt again

        # Proceed with assigning stats from the pool
        await self.assign_stats(ctx, pool)

    async def assign_stats(self, ctx, pool):
        stats = {}

        for stat in ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]:
            await ctx.send(f"Choose a value for {stat} from your pool: {pool}")
            stat_msg = await ctx.bot.wait_for(
                "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
            value = int(stat_msg.content)

            # Log the selection
            logger.info(f"User assigned {value} to {stat}")

            if value in pool:
                stats[stat] = value
                pool.remove(value)  # Remove the value from pool once assigned to a stat
            else:
                await ctx.send("Invalid choice. Try again.")
                continue  # Invalid selection, prompt again

        # Save final stats after assigning
        await ctx.send(f"Your final stats are: {stats}. Is this correct? (yes/no)")
        confirm_msg = await ctx.bot.wait_for(
            "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )

        if confirm_msg.content.lower() == "yes":
            self.character.stats = stats
            await ctx.send("Stats confirmed! Moving to class selection.")
            await self.choose_class(ctx)
        else:
            await ctx.send("Restarting rolling method...")
            await self.rolling_method(ctx)

    # Step #5: Choose Class
    async def choose_class(self, ctx):
        """
        Guide the user through class selection using ClassEnum.
        """
        # Retrieve all class display names from ClassEnum
        classes = [cls.display_name for cls in ClassEnum]
        await ctx.send(f"Choose a class from the following: {', '.join(classes)}")

        class_msg = await ctx.bot.wait_for(
            "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )

        # Match the user's input to a valid class
        chosen_class = next((cls for cls in ClassEnum if cls.display_name.lower() == class_msg.content.lower()), None)

        if chosen_class:
            await ctx.send(f"You selected {chosen_class.display_name}. Is this correct? (yes/no)")
            confirm_msg = await ctx.bot.wait_for(
                "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
            if confirm_msg.content.lower() == "yes":
                self.character.chosen_class = chosen_class
                await ctx.send("Class confirmed! Moving to race selection.")
                await self.choose_race(ctx)
            else:
                await ctx.send("Restarting class selection...")
                await self.choose_class(ctx)
        else:
            await ctx.send("Invalid class. Try again.")
            await self.choose_class(ctx)

    # Step #6: Choose Race
    async def choose_race(self, ctx):
        """
        Guide the user through race selection using RacesEnum.
        """
        await ctx.send(f"Choose a race from the following: {', '.join(RacesEnum.list())}")
        race_msg = await ctx.bot.wait_for(
            "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
        chosen_race = next((race for race in RacesEnum if race.value.lower() == race_msg.content.lower()), None)

        if chosen_race:
            await ctx.send(f"You selected {chosen_race.value}. Is this correct? (yes/no)")
            confirm_msg = await ctx.bot.wait_for(
                "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
            if confirm_msg.content.lower() == "yes":
                self.character.chosen_race = chosen_race
                await self.finalize_character(ctx, self.db_controller)
            else:
                await ctx.send("Restarting race selection...")
                await self.choose_race(ctx)
        else:
            await ctx.send("Invalid race. Try again.")
            await self.choose_race(ctx)

    async def finalize_character(self, ctx, db_controller):
        """
        Save the character to the database and confirm creation.
        """
        character = self.character
        try:
            # Validate the character before saving
            logger.info(f'Attempting to validate character: {character.name}')
            character.validate()

            validated_values = dict({
                "user_id": character.user_id,
                "stats": json.dumps({stat: value for stat, value in character.stats.items()}),
                "class": character.chosen_class.display_name,
                "race": character.chosen_race.display_name,
                "name": character.name
            })

            logger.debug(f"Validating:\n{validated_values}")

            # Convert to ORM Object
            orm_character = character.to_orm()

            # Save to the database
            db_controller.insert(orm_character)

            # Notify the user of successful creation
            await ctx.send(f'Character creation complete! Name: {character.name}, Stats: {json.dumps({stat:value for stat, value in character.stats.items()})}, '
                           f"Class: {character.chosen_class.display_name}, Race: {character.chosen_race.display_name}")
        except ValueError as e:
            logger.error(f"Error on character validation:\n{traceback.format_exc()}")
            await ctx.send(f"Character validation failed: {e}")
        except Exception as e:
            logger.error(f"Exception on finalizing character:\n{traceback.format_exc()}")
            await ctx.send(f"Failed to save character: {e}")