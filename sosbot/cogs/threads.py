"""
Commands to handle saving, retrieving, and managing conversations (replies and threads).
"""
import logging
import os
# pylint: disable=no-name-in-module
from typing import Dict, Iterable
import pytz

from disnake import Thread, Message, MessageReference, AllowedMentions, File
from disnake.ext.commands import command, Cog, Context, Command

from sosbot.bot import (SOSBot, CONFIG_DISCORD_SAVEDIR)

logging.basicConfig(level=logging.INFO)

ALPHAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SHEETS = [
    "A-E", "F-J", "K-O", "P-T", "U-Z"
]


class Conversations(Cog, name="Conversation Commands"):
    """Cog containing logic for scraping and saving information from threads"""

    def __init__(self, bot: SOSBot):
        """Initialize the cog, including the gspread service used to access the Sheet"""

        self.bot = bot

    @command(name="save-convo")
    async def save_convo(self, ctx: Context):
        """Find all messages in the reply stream
        (backtracking from the current message to the start of the reply stream).

        Given that starting point, look through the message history from that point forward and
        track any messages that are replies to this original message (or one of its own replies).
        Then, save this set of messages to a file with the given title for later reference. The
        file will also be attached as a reply to this command message.

        USAGE: !save-convo CONVERSATION TITLE
        """
        command_message: Message = ctx.message
        cmd: Command = ctx.command
        convo_title = command_message.content[len(cmd.name) + 2:].strip()
        if len(convo_title) < 1:
            await command_message.reply(f"Usage: !{cmd.name} CONVERSATION TITLE")
            return

        starting_point, in_thread = await self._find_thread(command_message, ctx)
        if starting_point is not None:
            with ctx.typing():
                storage_path = self._format_storage_path(ctx, ctx.channel.name, convo_title)
                file = self._write_messages(
                    sorted(in_thread.values(), key=lambda x: x.created_at),
                    storage_path,
                    convo_title,
                    ctx
                )

                await command_message.reply(
                    f"Saved conversation to: {ctx.guild.name}/{ctx.channel.name}/{convo_title}",
                    file=file
                )
        else:
            await command_message.reply("Cannot find a conversation to save!")

    @command(name="make-thread")
    async def make_thread(self, ctx: Context):
        """Find all messages in the reply stream
        (backtracking from the current message to the start of the reply stream).

        Given that starting point, look through the message history from that point forward and
        track any messages that are replies to this original message (or one of its own replies).
        Then, use this set of messages to construct a new Discord thread with the given title.

        USAGE: !make-thread THREAD TITLE
        """

        command_message: Message = ctx.message
        cmd: Command = ctx.command
        thread_title = command_message.content[len(cmd.name)+2:].strip()

        starting_point, in_thread = await self._find_thread(command_message, ctx)
        if starting_point is not None:
            with ctx.typing():
                allowed_mentions = AllowedMentions(
                    everyone=True,
                    users=True,
                    roles=True,
                    replied_user=True
                )
                fork_point = await command_message.reply(
                    f"Thread: **{thread_title}**",
                    allowed_mentions=allowed_mentions
                )

                thread: Thread = await ctx.channel.create_thread(
                    name=thread_title, message=fork_point
                )

                sent = {}
                for m in sorted(in_thread.values(), key=lambda x: x.created_at):
                    ref = m.reference
                    if ref is not None:
                        ref = sent[ref.message_id]

                    files = []
                    for a in m.attachments:
                        files.append(await a.to_file())

                    tm = await thread.send(
                        f"<@{m.author.id}> said: {m.content}",
                        files=files,
                        reference=ref,
                        allowed_mentions=allowed_mentions
                    )

                    sent[m.id] = tm.to_reference()
        else:
            await command_message.reply(
                "This message is not a response! Try responding to a message with this command."
            )

    @command(name="save-thread")
    async def save_thread(self, ctx: Context):
        """Retrieve the message contents of a Discord thread, and save it to a file with the
        thread's title.

        Usage: !save-thread
        """
        command_message: Message = ctx.message
        channel = command_message.channel

        if isinstance(channel, Thread):
            messages = await channel.history(limit=500, oldest_first=True).flatten()
            storage_path = self._format_storage_path(ctx, channel.parent.name, channel.name)

            file = self._write_messages(messages, storage_path, channel.name, ctx)

            await command_message.reply(
                f"Saved conversation to: {ctx.guild.name}/{channel.parent.name}/{channel.name}",
                file=file
            )
        else:
            await command_message.reply("Cannot save. This is not a thread! Try `!save-convo`.")

    @command(name="list-convos")
    async def list_convos(self, ctx: Context):
        """Retrieve the list of saved conversations for the current channel on the current server.

        Usage: !list-convos
        """
        storage_dir = self._format_storage_dir(ctx, ctx.channel.name)
        fnames = os.listdir(storage_dir)
        response = "\n".join([f"* {os.path.splitext(f)[0]}" for f in fnames])

        await ctx.reply(f"The following conversations have been saved:\n\n{response}")

    @command(name="load-convo")
    async def load_convo(self, ctx: Context):
        """Retrieve the list of threads for the current channel on the current server.

        Usage: !load-convo TITLE
        """
        command_message: Message = ctx.message
        cmd: Command = ctx.command
        convo_path = command_message.content[len(cmd.name) + 2:].strip()
        if len(convo_path) < 1:
            await command_message.reply(f"Usage: !{cmd.name} CHANNEL/TITLE\n"
                                        f"Try !list-convos for more.")
            return

        docpath = self._format_storage_path(ctx, ctx.channel.name, convo_path)

        if os.path.exists(docpath):
            file = File(docpath)
            await ctx.reply(file=file)
        else:
            await ctx.reply(f"No conversation found for that channel/title")

    def _format_storage_dir(self, ctx: Context, channel_subpath: str) -> str:
        """Format an appropriate storage directory based on server name and channel name.
        """
        storage_root = self.bot.discord.config.get(CONFIG_DISCORD_SAVEDIR) or os.path.join(
            os.environ['HOME'], 'sosbot-saved'
        )

        return os.path.join(storage_root, ctx.guild.name, channel_subpath)

    def _format_storage_path(self, ctx: Context, channel_subpath: str, title: str) -> str:
        """Format an appropriate storage path based on server name, channel name, and a
        title given by the user. The result will be a path to a Markdown file.
        """
        storage_root = self.bot.discord.config.get(CONFIG_DISCORD_SAVEDIR) or os.path.join(
            os.environ['HOME'], 'sosbot-saved'
        )

        return os.path.join(
            storage_root, ctx.guild.name, channel_subpath, title + ".md"
        )

    @staticmethod
    def _write_messages(
            messages: Iterable[Message], storage_path: str, title: str,
            ctx: Context
    ) -> File:
        """Write a list of messages to a Markdown-formatted file, and return a File object
        suitable to post in a Discord message.
        """
        if not os.path.isdir(os.path.dirname(storage_path)):
            os.makedirs(os.path.dirname(storage_path))

        last_date = None
        with open(storage_path, 'w') as filestore:
            filestore.write(
                f"# {title}\n\n"
                f"**NOTE:** This conversation was recorded in {ctx.channel.name}, "
                f"on server {ctx.guild.name}.\n"
            )

            for message in messages:
                dt = message.created_at.replace(tzinfo=pytz.timezone("US/Central"))
                datestr = dt.strftime("%x")
                timestr = dt.strftime("%X")
                if datestr != last_date:
                    filestore.write(f"\n## {datestr}\n")
                    last_date = datestr

                filestore.write(
                    f"* {timestr} @{message.author.display_name}: {message.clean_content}\n"
                )

        return File(storage_path, description=title)

    @staticmethod
    async def _find_thread(command_message: Message, ctx: Context):
        message: Message = command_message
        starting_point: MessageReference = message.reference
        print(f"Message: `{message.content}` in reply to: {starting_point.message_id}")

        in_thread: Dict[int, Message] = {}
        if starting_point is not None:
            last_start_point = starting_point
            while starting_point is not None:
                message = await ctx.channel.fetch_message(starting_point.message_id)
                in_thread[starting_point.message_id] = message
                last_start_point = starting_point
                starting_point = message.reference

            starting_point = last_start_point

        else:
            in_thread[message.id] = message

        async for m in ctx.channel.history(after=message.created_at, oldest_first=True):
            if m.reference is not None and m.reference.message_id in in_thread:
                in_thread[m.id] = m

        return starting_point, in_thread


