"""Basic startup script for the SOSBot Discord bot"""

import click

from sosbot.bot import load_bot
from sosbot.cogs.definitions import DefinitionCog
from sosbot.cogs.datasets import DatasetCog
from sosbot.cogs.threads import ThreadsCog
from sosbot.cogs.hello import HelloCommand


@click.command()
def start():
    """Startup the bot"""

    bot = load_bot()
    bot.discord.add_cog(HelloCommand(bot))
    # bot.discord.add_cog(DefinitionCog(bot))
    # bot.discord.add_cog(DatasetCog(bot))
    # bot.discord.add_cog(ThreadsCog(bot))

    print("Starting sosbot for Discord.")
    bot.discord.start()
