import discord
from discord.ext import commands


class HelpAO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="HelpAO")
    async def help_ao(self, ctx):
        """Display help for available commands, separated by role (User, Staff, DM, Channel-Specific)."""

        # Check if user is in a staff or DM role
        is_staff = any(role.name.lower() in ["staff", "admin"] for role in ctx.author.roles)
        is_dm = any(role.name.lower() == "dm" for role in ctx.author.roles)

        # Define commands for each role
        user_commands = """
        **User Commands:**
        - !HelpAO: Show available commands
        - !inventory: View Ysolde's shop inventory
        - !buy <item> <quantity>: Buy items from Ysolde
        - !sell <item> <quantity>: Sell items to Ysolde
        - !recent: View your recent transactions with Ysolde
        """

        staff_commands = """
        **Staff Commands:**
        - !ban <user>: Ban a user from the server
        - !kick <user>: Kick a user from the server
        - !clear <amount>: Clear messages from the channel
        - !warn <user> <reason>: Warn a user for inappropriate behavior
        """

        dm_commands = """
        **DM Commands:**
        - !start_adventure: Start a new adventure
        - !end_adventure: End the current adventure
        - !spawn <monster>: Spawn a monster for the players
        - !give_item <player> <item>: Give an item to a player
        """

        # Channel-Specific Commands (commands that need to be used in specific channels)
        channel_specific_commands = """
        **Channel-Specific Commands:**
        - !shop (Channel: #marketplace): View Ysolde's shop inventory in the marketplace channel.
        - !battle (Channel: #battle-arena): Start a battle in the battle arena channel.
        - !quest (Channel: #quest-board): View or post new quests in the quest board channel.
        """

        # Build the help message
        help_message = "**Available Commands:**\n"
        help_message += user_commands

        if is_staff:
            help_message += staff_commands

        if is_dm:
            help_message += dm_commands

        help_message += channel_specific_commands

        # Send the help message to the user
        await ctx.send(help_message)


async def setup(bot):
    """Setup function to add the HelpAO cog."""
    await bot.add_cog(HelpAO(bot))
