"""Basic Hello, World type commands for the bot library"""

from disnake.ext.commands import Cog, command, Context


class HelloCommand(Cog, name="\n\nHello Commands"):
    """Basic commands to test bot features. Similar to Hello, World programs."""

    @command(name="hi")
    @staticmethod
    async def say(ctx: Context, *, name: str):
        """Just say hi, and repeat the message the user sent."""

        await ctx.send(f"Hi {ctx.message.author.display_name} ({name}).")
