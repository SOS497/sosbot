#!/usr/bin/env python

from sauced.bot import load_bot
from sauced.cogs.definitions import DefinitionCog
from sauced.cogs.datasets import DatasetCog

bot = load_bot()
bot.discord.add_cog(DefinitionCog(bot))
bot.discord.add_cog(DatasetCog(bot))

print("Starting sauced Discord bot.")
bot.discord.start()
