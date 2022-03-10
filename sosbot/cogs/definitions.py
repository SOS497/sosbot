"""Commands to handle saving, retrieving, and maintaining term definitions into a Google Sheet"""
import logging
from datetime import datetime as dt
# pylint: disable=no-name-in-module
from typing import Literal
from math import floor

from disnake import Message
from disnake.ext import commands

from sosbot.bot import (SOSBot, CONFIG_DEFINITION_GSHEET)

logging.basicConfig(level=logging.INFO)

ALPHAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SHEETS = [
    "A-E", "F-J", "K-O", "P-T", "U-Z"
]


class DefinitionCog(commands.Cog, name="\n\nGlossary"):
    """Cog containing logic for managing and retrieving term definitions"""

    def __init__(self, bot: SOSBot):
        """Initialize the cog, including the gspread service used to access the Sheet"""

        self.bot = bot.discord.bot
        self.definitions = bot.google.config.get(CONFIG_DEFINITION_GSHEET)
        self.sheets_service = bot.google.get_gspread()

    @commands.command("define")
    async def save_definition(self,
                              ctx: commands.Context,
                              term: str,
                              _as: Literal['as'],
                              *,
                              definition: str):
        """
        Set the definition of a term

        Usage: !define <term> as <the-definition>
        Usage: !define "<term> <words>" as <the-definition>
        """

        message: Message = ctx.message
        if message.author.id != self.bot.user.id:
            try:
                idx = ALPHAS.index(term[0].upper())
                key = SHEETS[floor(idx / 5)]
                async with ctx.typing():
                    spreadsheet = self.sheets_service.open_by_key(self.definitions)
                    sheet = spreadsheet.worksheet(key)
                    rows = sheet.get_all_records()

                    for row in rows:
                        if len(row) > 0 and row["Term"].lower() == term.lower():
                            await message.reply(f"{term} is already defined!")
                            return

                    sheet.append_row(
                        [term, definition, message.author.display_name, dt.now().strftime("%x")])
                    sheet.sort((1, 'asc'), range=f"A2:D{len(rows) + 2}")

                await message.reply(f"'{term}' is now defined as '{definition}'")
            # pylint: disable=broad-except
            except Exception as error:
                print(error)
                try:
                    await message.reply("Sorry, an error has occurred.")
                # pylint: disable=broad-except
                except Exception as safe_error:
                    print(safe_error)

    @commands.command("undefine")
    async def clear_definition(self, ctx: commands.Context, term: str):
        """
        Clear the definition of a term

        Usage: !undefine <term>
        Usage: !undefine "<term> <words>"
        """

        if ctx.author.id != self.bot.user.id:
            try:
                idx = ALPHAS.index(term[0].upper())
                key = SHEETS[floor(idx / 5)]
                term_index = -1
                async with ctx.typing():
                    spreadsheet = self.sheets_service.open_by_key(self.definitions)
                    sheet = spreadsheet.worksheet(key)
                    rows = sheet.get_all_records()

                    for idx, row in enumerate(rows):
                        if len(row) > 0 and row["Term"].lower() == term.lower():
                            term_index = idx
                            break

                if term_index > -1:
                    sheet.delete_row(term_index + 2)
                    await ctx.reply(f"The definition of '{term}' has been removed.")
                else:
                    await ctx.reply(f"{term} was not defined!")
            # pylint: disable=broad-except
            except Exception as error:
                print(error)
                try:
                    await ctx.reply("Sorry, an error has occurred.")
                # pylint: disable=broad-except
                except Exception as safe_error:
                    print(safe_error)

    @commands.command("whatis")
    async def lookup_definition(self, ctx: commands.Context, term: str):
        """
        Retrieve the definition of a term.

        Usage: !whatis <term>
        Usage: !whatis "<term> <words>"
        """
        if ctx.author.id != self.bot.user.id:
            try:
                idx = ALPHAS.index(term[0].upper())
                key = SHEETS[floor(idx / 5)]
                response = None
                async with ctx.typing():
                    spreadsheet = self.sheets_service.open_by_key(self.definitions)
                    sheet = spreadsheet.worksheet(key)
                    rows = sheet.get_all_records()

                    for row in rows:
                        if len(row) > 0 and row["Term"].lower() == term.lower():
                            response = f"**{term}**: '{row['Definition']}'" \
                                       f"\n    *({row['Author']}, {row['Date']})*."
                            break

                if response is None:
                    await ctx.reply(
                        f"'{term}' is not defined, but this might help:"
                        f"\nhttps://duckduckgo.com/?q=%22{term}%22+USD497+KSDE+Kansas"
                    )
                else:
                    await ctx.reply(response)
            # pylint: disable=broad-except
            except Exception as error:
                print(error)
                try:
                    await ctx.reply("Sorry, an error has occurred.")
                # pylint: disable=broad-except
                except Exception as safe_error:
                    print(safe_error)
