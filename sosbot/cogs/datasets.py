"""Commands to handle saving, retrieving, and maintaining items associated with different datasets
into a Google Sheet"""
import logging
import re
from datetime import datetime as dt
from math import floor

# pylint: disable=no-name-in-module
from disnake.ext import commands
from disnake.message import Message

from sosbot.bot import (SOSBot, CONFIG_DATASET_GSHEET)

logging.basicConfig(level=logging.INFO)

ALPHAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SHEETS = [
    "A-E", "F-J", "K-O", "P-T", "U-Z"
]


class DatasetCog(commands.Cog, name="\n\nDoc Collections / Datasets"):
    """Cog that collects commands related to managing and retrieving dataset information"""

    def __init__(self, bot: SOSBot):
        """Initialize the cog, including the gspread service used to access the Sheet"""
        self.bot = bot.discord.bot
        self.datasets = bot.google.config.get(CONFIG_DATASET_GSHEET)
        self.sheets_service = bot.google.get_gspread()

    @commands.command("set-dataset")
    async def set_dataset(self, ctx: commands.Context):
        """
        Associates a URL with a dataset

        Usage: !set-dataset <dataset> <url> <description>

        NOTE: dataset name CANNOT contain spaces.
        """

        message: Message = ctx.message
        if message.author.id != self.bot.user.id:
            try:
                match = re.match(r"!set-dataset\s+([\S]+)\s+([\S]+)(\s+(.*))?", message.content)
                if not match:
                    await message.reply(f"Didn't understand: '{message.content}'")
                    return

                dataset = match[1].strip()
                url = match[2].strip()
                description = match[3].strip()
                async with ctx.typing():
                    idx = ALPHAS.index(dataset[0].upper())
                    key = SHEETS[floor(idx / 5)]
                    spreadsheet = self.sheets_service.open_by_key(self.datasets)
                    sheet = spreadsheet.worksheet(key)
                    rows = sheet.get_all_records()

                    sheet.append_row([
                        dataset, url, description, message.author.display_name,
                        dt.now().strftime("%x")
                    ])
                    sheet.sort((1, 'asc'), range=f"A2:E{len(rows) + 2}")

                await message.reply(f"'{dataset}' now includes '{url}'")
            # pylint: disable=broad-except
            except Exception as error:
                print(error)
                try:
                    await message.reply("Sorry, an error has occurred.")
                # pylint: disable=broad-except
                except Exception as safe_error:
                    print(safe_error)

    @commands.command("clear-dataset")
    async def remove_from_dataset(self, ctx: commands.Context):
        """
        Clear a URL from a dataset

        Usage: !clear-dataset <dataset> <URL>

        NOTE: dataset name CANNOT contain spaces.
        """

        message: Message = ctx.message
        if message.author.id != self.bot.user.id:
            try:
                match = re.match(r"!clear-dataset\s+([\S]+)\s+([\S]+)\s*", message.content)
                if not match:
                    await message.reply(f"Didn't understand: '{message.content}'")
                    return

                dataset = match[1].strip()
                url = match[2].strip()
                found_index = -1
                async with ctx.typing():
                    idx = ALPHAS.index(dataset[0].upper())
                    key = SHEETS[floor(idx / 5)]
                    spreadsheet = self.sheets_service.open_by_key(self.datasets)
                    sheet = spreadsheet.worksheet(key)
                    rows = sheet.get_all_records()

                    for idx, row in enumerate(rows):
                        if len(row) > 1 \
                                and row["Dataset"].lower() == dataset.lower() \
                                and row["URL"].lower() == url.lower():
                            found_index = idx
                            break

                if found_index > -1:
                    sheet.delete_row(found_index + 2)
                    await message.reply(f"{url} has been removed from {dataset}.")
                else:
                    await message.reply(f"{url} was not found in {dataset}!")
            # pylint: disable=broad-except
            except Exception as error:
                print(error)
                try:
                    await message.reply("Sorry, an error has occurred.")
                # pylint: disable=broad-except
                except Exception as safe_error:
                    print(safe_error)

    @commands.command("dataset")
    async def get_dataset(self, ctx: commands.Context):
        """
        Retrieve the links in a dataset.

        Usage: !dataset <dataset-name>

        NOTE: dataset name CANNOT contain spaces.
        """

        message: Message = ctx.message
        if message.author.id != self.bot.user.id:
            try:
                match = re.match(r"!dataset\s+([\S]+)\s*", message.content)
                if not match:
                    await message.reply(f"Didn't understand: '{message.content}'")
                    return

                dataset = match[1].strip()
                ds_rows = []
                async with ctx.typing():
                    idx = ALPHAS.index(dataset[0].upper())
                    key = SHEETS[floor(idx / 5)]
                    spreadsheet = self.sheets_service.open_by_key(self.datasets)
                    sheet = spreadsheet.worksheet(key)
                    rows = sheet.get_all_records()

                    for row in rows:
                        if len(row) > 0 and row["Dataset"].lower() == dataset.lower():
                            ds_rows.append(
                                f"{row['Description']} *({row['Author']}, {row['Date']})*\n"
                                f"{row['URL']}"
                            )

                if len(ds_rows) > 0:
                    response = f"Dataset **{dataset}** contains {len(ds_rows)} entries:\n\n" + \
                               "\n\n".join(ds_rows)

                    await message.reply(response)
                else:
                    await message.reply(f"'{dataset}' has no associated content!")
            # pylint: disable=broad-except
            except Exception as error:
                print(error)
                try:
                    await message.reply("Sorry, an error has occurred.")
                # pylint: disable=broad-except
                except Exception as safe_error:
                    print(safe_error)

    @commands.command("datasets")
    async def list_datasets(self, ctx: commands.Context):
        """
        Retrieve the list of available datasets.

        Usage: !datasets
        """

        message: Message = ctx.message
        if message.author.id != self.bot.user.id:
            try:
                dss = {}
                async with ctx.typing():
                    for key in SHEETS:
                        spreadsheet = self.sheets_service.open_by_key(self.datasets)
                        sheet = spreadsheet.worksheet(key)
                        rows = sheet.get_all_records()

                        for row in rows:
                            if len(row) > 0:
                                dataset = row['Dataset']
                                count = dss.get(dataset) or 0
                                dss[dataset] = count + 1

                response = []
                for dataset, count in dss.items():
                    response.append(f"* **{dataset}** ({count} items)")

                await message.reply(
                    f"{len(dss)} datasets found:\n\n" +
                    "\n".join(dss) +
                    "\n\nUse !dataset <name> for more information"
                )
            # pylint: disable=broad-except
            except Exception as error:
                print(error)
                try:
                    await message.reply("Sorry, an error has occurred.")
                # pylint: disable=broad-except
                except Exception as safe_error:
                    print(safe_error)
