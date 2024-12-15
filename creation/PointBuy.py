import discord
from discord.ui import View
from entities.Stats import StatsEnum


class PointBuy:
    def __init__(self, interaction: discord.Interaction, character):
        self.interaction = interaction
        self.character = character
        self.points = 27
        self.stats = {stat: 8 for stat in StatsEnum}
        self.cost_table = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}

    async def start(self):
        """
        Begin the Point Buy process.
        """
        await self.interaction.response.send_message("Customize your stats using Point Buy:", ephemeral=True)
        await self.update_view()

    async def update_view(self):
        """
        Update the dropdown view to reflect the current stats and remaining points.
        """
        view = View()

        # Add dropdowns for each stat
        for stat in StatsEnum:
            options = [
                discord.SelectOption(label=f"{value}", value=str(value))
                for value in range(8, 16)
                if self.points - (self.cost_table[value] - self.cost_table[self.stats[stat]]) >= 0
            ]
            view.add_item(discord.ui.Select(
                options=options,
                placeholder=f"Set {stat.display_name} (current: {self.stats[stat]})",
                custom_id=f"stat_{stat.value}",
                row=0
            ).callback(self.adjust_stat))

        # Add Finish Button
        view.add_item(discord.ui.Button(
            label="Finish",
            style=discord.ButtonStyle.primary,
            custom_id="finish_button",
            row=1
        ).callback(self.finish_point_buy))

        await self.interaction.edit_original_response(
            content=f"**Remaining Points**: {self.points}\n"
                    f"**Stats**: {', '.join(f'{stat.display_name}: {value}' for stat, value in self.stats.items())}",
            view=view
        )

    async def adjust_stat(self, interaction: discord.Interaction, value):
        """
        Adjust the value of a stat and update the remaining points.
        """
        stat = StatsEnum[value.custom_id.split("_")[1]]  # Extract stat from custom_id
        new_value = int(value.values[0])
        self.points += self.cost_table[self.stats[stat]] - self.cost_table[new_value]
        self.stats[stat] = new_value
        await self.update_view()

    async def finish_point_buy(self, interaction: discord.Interaction):
        """
        Finalize the Point Buy and pass the character stats back to the main flow.
        """
        self.character.stats = self.stats
        await interaction.response.send_message("Stats confirmed! Returning to main character creation flow.")
        return self.character
