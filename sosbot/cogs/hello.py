from disnake.ext.commands import Cog, command, Context


class HelloCommand(Cog):
    @command(name="repeat")
    async def say(self, ctx: Context):
        await ctx.send(f"Hi {ctx.message.author.display_name}")

