"""Commands to handle saving, retrieving, and maintaining term definitions into a Google Sheet"""
import logging

# pylint: disable=no-name-in-module
from disnake.ext import commands
from disnake.ext.commands import Cog, Context

from sosbot.bot import (SOSBot)

logging.basicConfig(level=logging.INFO)

ALPHAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SHEETS = [
    "A-E", "F-J", "K-O", "P-T", "U-Z"
]


class ThreadsCog(Cog):  # , name="Thread Commands"):
    """Cog containing logic for scraping and saving information from threads"""

    def __init__(self, bot: SOSBot):
        """Initialize the cog, including the gspread service used to access the Sheet"""

        self.bot = bot.discord.bot

    @commands.Cog.listener()
    async def on_message(self, ctx: Context):
        """
        Capture a thread of messages

        Usage: !capture
        """

        try:
            await ctx.send("Thread Hi")
        # pylint: disable=broad-except
        except Exception as error:
            print(error)
            return "Sorry, an error has occurred."

