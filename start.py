#!/usr/bin/env python

"""Basic startup script for the SOSBot Discord bot"""

from sosbot.bot import load_bot
from sosbot.cogs.definitions import DefinitionCog
from sosbot.cogs.datasets import DatasetCog

bot = load_bot()
bot.discord.add_cog(DefinitionCog(bot))
bot.discord.add_cog(DatasetCog(bot))

print("Starting sosbot for Discord.")
bot.discord.start()
