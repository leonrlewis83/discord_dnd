# TODO: Add Server side debug logging capabilities
import random
import logging
import json
from discord.ext.commands import Context
from entities.Character import CharacterBuilder
from entities.Classes import ClassEnum
from entities.Races import RacesEnum
from entities.Stats import StatsEnum
from utils.DatabaseController import DatabaseController

logger = logging.getLogger("bot.character")
async def finalize_character(ctx, db_controller, character: CharacterBuilder):
    """
    Save the character to the database and confirm creation.
    """
    try:
        # Validate the character before saving
        logger.info(f'Attempting to validate character: {character}')
        character.validate()

        # Save to the database
        db_controller.insert("characters", {
            "user_id": character.user_id,
            "stats": json.dumps({stat.name: value for stat, value in character.stats.items()}),
            "class": character.chosen_class.display_name,
            "race": character.chosen_race.value
        })

        # Notify the user of successful creation
        await ctx.send(f'Character creation complete! Stats: {json.dumps({stat.name:value for stat, value in character.stats.items()})}, '
                       f"Class: {character.chosen_class.display_name}, Race: {character.chosen_race.value}")
    except ValueError as e:
        await ctx.send(f"Character validation failed: {e}")
    except Exception as e:
        await ctx.send(f"Failed to save character: {e}")

class CharacterCreation:
    def __init__(self, db_controller: DatabaseController):
        self.db_controller = db_controller

    async def newchar(self, ctx: Context):
        user_id = ctx.author.id
        character = CharacterBuilder(user_id=user_id)
        # Proceed to step #2
        await ctx.send("Choose your stat generation method: (1) Standard Point Buy or (2) Rolling")
        msg = await ctx.bot.wait_for(
            "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )

        if msg.content == "1":
            await self.standard_point_buy(ctx, character)
        elif msg.content == "2":
            await self.rolling_method(ctx, character)
        else:
            await ctx.send("Invalid choice. Please start over by typing `!newchar`.")

    # Step #3: Standard Point Buy
    # This method is messy, and needs some TLC.
    # TODO: Update method with more efficient way of handling point assignments.
    async def standard_point_buy(self, ctx: Context, character: CharacterBuilder):
        """
        Guide the user through the Standard Point Buy system for assigning stats.

        :param ctx: Discord context for sending and receiving messages.
        :param character: The CharacterBuilder instance being constructed.
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
            character.stats = stats
            await ctx.send("Stats confirmed! Moving to class selection.")
            await self.choose_class(ctx, character)
        else:
            await ctx.send("Restarting point buy...")
            await self.standard_point_buy(ctx, character)


    # Step #4: Rolling Method
    async def rolling_method(self, ctx: Context, character: CharacterBuilder):
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

        await ctx.send(f"Here is your grid:\n{grid[:3]}\n{grid[3:6]}\n{grid[6:9]}")
        pool = []

        for _ in range(2):
            await ctx.send("Select a row, column, or diagonal (e.g., Row 1):")
            selection_msg = await ctx.bot.wait_for(
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
        # TODO: Look - more references to the stat array.
        # BUG: Found issue with duplicate roll values in the pool
        stats = {}
        for stat in ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]:
            await ctx.send(f"Choose a value for {stat} from your pool: {pool}")
            stat_msg = await ctx.bot.wait_for(
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
        confirm_msg = await ctx.bot.wait_for(
            "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )

        if confirm_msg.content.lower() == "yes":
            await ctx.send("Stats confirmed! Moving to class selection.")
            await self.choose_class(ctx, character)
        else:
            await ctx.send("Restarting rolling method...")
            await self.rolling_method(ctx)


    # Step #5: Choose Class
    async def choose_class(self, ctx: Context, character: CharacterBuilder):
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
                character.chosen_class = chosen_class
                await ctx.send("Class confirmed! Moving to race selection.")
                await self.choose_race(ctx, character)
            else:
                await ctx.send("Restarting class selection...")
                await self.choose_class(ctx, character)
        else:
            await ctx.send("Invalid class. Try again.")
            await self.choose_class(ctx, character)


    # Step #6: Choose Race
    async def choose_race(self, ctx: Context, character: CharacterBuilder):
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
                character.chosen_race = chosen_race
                await finalize_character(ctx, self.db_controller, character)
            else:
                await ctx.send("Restarting race selection...")
                await self.choose_race(ctx, character)
        else:
            await ctx.send("Invalid race. Try again.")
            await self.choose_race(ctx, character)
    