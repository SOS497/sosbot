from ruamel.yaml import YAML
from os import environ
from os.path import join
from google.oauth2 import service_account
from discord.ext import commands
from googleapiclient import discovery
import gspread

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
    def __init__(self, data: dict):
        self._token = data.pop(CONFIG_DISCORD_TOKEN, None)
        self.config = data
        self.bot = commands.Bot(command_prefix='!', description="SOS bot -> type `!help` to get started!")

    def add_cog(self, cog: commands.Cog):
        self.bot.add_cog(cog)

    def start(self):
        self.bot.run(self._token)


class GoogleAccess:
    def __init__(self, data: dict):
        creds_file = data.pop(CONFIG_GOOGLE_SERVICE_CREDS, None)
        self.config = data

        self._google_creds = service_account.Credentials.from_service_account_file(
            creds_file, scopes=GOOGLE_SCOPES)

    def get_service(self, service_name: str, service_version: str):
        return discovery.build(service_name, service_version, credentials=self._google_creds)

    def get_gspread(self) -> gspread.Client:
        return gspread.authorize(self._google_creds)


class SaucedBot:
    def __init__(self, data: dict):
        self.discord = DiscordBot(data[CONFIG_DISCORD_SECTION])
        self.google = GoogleAccess(data[CONFIG_GOOGLE_SECTION])


def load_bot(config_yml: str = DEFAULT_CONFIG) -> SaucedBot:
    with open(config_yml, 'r') as yf:
        data = YAML().load(yf)
        return SaucedBot(data)

