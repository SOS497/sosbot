"""Bootstrap the bot by reading configuration and setting up the Bot + Google access."""
from os import environ
from os.path import join

import gspread
from disnake.ext import commands
from google.oauth2 import service_account
from googleapiclient import discovery
from ruamel.yaml import YAML

#######################################################################################
# Important notes about authenticating gspread (used for Google Sheets access):
#      https://docs.gspread.org/en/latest/oauth2.html#for-bots-using-service-account
#######################################################################################
DEFAULT_CONFIG = join(environ["HOME"], ".config/sosbot/config.yaml")
GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://spreadsheets.google.com/feeds',
]

CONFIG_DISCORD_SECTION = "discord"
CONFIG_GOOGLE_SECTION = "google"

CONFIG_DISCORD_TOKEN = "token"

CONFIG_DEFINITION_GSHEET = "definitions-sheet"
CONFIG_DATASET_GSHEET = "datasets-sheet"
CONFIG_GOOGLE_SERVICE_CREDS = "creds-json"


class DiscordBot:
    """Bot class used to house Discord bot state and convenience logic."""

    def __init__(self, data: dict):
        """Setup Discord bot and save app-specific configuration for later reference."""

        self._token = data.pop(CONFIG_DISCORD_TOKEN, None)
        self.config = data
        self.bot = commands.Bot(
            command_prefix='!', description="SOS bot -> type `!help` to get started!"
        )

    def add_cog(self, cog: commands.Cog):
        """Register a new cog (suite of commands) to the bot"""

        self.bot.add_cog(cog)

    def start(self):
        """Start the bot listening in Discord"""

        self.bot.run(self._token)


class GoogleAccess:
    """
    Convenience class used to house configuration, state and logic related to accessing
    Google storage and such.
    """

    def __init__(self, data: dict):
        """Setup the credentials for use with Google services and save additional config for later
        reference in the application."""

        creds_file = data.pop(CONFIG_GOOGLE_SERVICE_CREDS, None)
        self.config = data

        self._google_creds = service_account.Credentials.from_service_account_file(
            creds_file, scopes=GOOGLE_SCOPES)

    def get_service(self, service_name: str, service_version: str):
        """Setup a Google APIs service using the credentials we have stored."""

        return discovery.build(service_name, service_version, credentials=self._google_creds)

    def get_gspread(self) -> gspread.Client:
        """Setup a gspread connection using the credentials we have stored."""

        return gspread.authorize(self._google_creds)


# pylint: disable=too-few-public-methods
class SOSBot:
    """
    Outer class used to orchestrate setup of Discord and Google connections, and make them
    available to the application.
    """

    def __init__(self, data: dict):
        """Setup the Discord and Google connections using the related config sections."""

        self.discord = DiscordBot(data[CONFIG_DISCORD_SECTION])
        self.google = GoogleAccess(data[CONFIG_GOOGLE_SECTION])


def load_bot(config_yml: str = DEFAULT_CONFIG) -> SOSBot:
    """Read configuration from disk and use it to start a new bot instance"""

    with open(config_yml, 'r', encoding='utf-8') as yaml_file:
        data = YAML().load(yaml_file)
        return SOSBot(data)
