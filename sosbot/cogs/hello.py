import json
from typing import List

from disnake import Message, MessageReference
from disnake.ext.commands import Cog, command, Context, slash_command


class HelloCommand(Cog):
    @command(name="hi")
    async def say(self, ctx: Context):
        message: Message = ctx.message
        messages = [message]

        ref: MessageReference = message.reference
        while ref is not None:
            message = await ctx.channel.fetch_message(ref.message_id)
            messages.append(message)
            ref = message.reference

        lines = []
        for m in messages:
            lines.append(f"{m.created_at} **{m.author.display_name}:** {m.content}")

        response = "\n".join(lines)
        await ctx.send(f"Hi {ctx.message.author.display_name}. Reply thread:\n\n{response}")

