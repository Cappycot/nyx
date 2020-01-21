"""
Here we need to replace the default help command to be able to deal with
disambiguations while feeding same or similar information to HelpFormatters...

Possible solutions for accounting for disambiguation information:
 - Injecting the cog name (lowercase probably) into the Context prefix.

Notes:
 - Command signature is in the format [name|alias] <param> [param]
"""

import re

from discord.ext import commands
from discord.ext.commands import Group, HelpCommand, DefaultHelpCommand, \
    MinimalHelpCommand
from discord.ext.commands.errors import CommandError
from discord.ext.commands.view import StringView


class DefaultNyxHelpCommand(DefaultHelpCommand):

    def __init__(self, **options):
        super().__init__(**options)
        self._ref_command = None

    def get_bot_mapping(self):
        mapping = super().get_bot_mapping()
        namespace_none = self.context.bot.get_namespace(None)
        if namespace_none is not None:
            mapping[None] = [a for a in namespace_none.values()]
        return mapping

    async def command_not_found(self, string):
        # self.context  # has all info
        # check for disambiguation
        # print(self._ref_command)
        view = StringView(self._ref_command)

        invoker = view.get_word().lower()

        bot = self.context.bot
        command = None
        disambiguation = bot.get_disambiguation(invoker)
        namespace = bot.get_namespace(invoker)

        if namespace is not None:
            view.skip_ws()
            # We'll need to affix the namespace name to the prefix if we
            # get a working command to invoke.
            namespace_name = invoker
            invoker = view.get_word().lower()
            if invoker:
                command = namespace.get(invoker)
                self.context.prefix += namespace_name + " "
        elif disambiguation is not None:
            if len(disambiguation) == 1:
                command = list(disambiguation.values())[0]
            elif len(disambiguation) > 1 and self.context.guild is not None:
                command = bot.get_guild_data(
                    self.context.guild).command_map.get(invoker)

        if command is not None:
            # TODO: Perform search for subcommands.
            if isinstance(command, Group):
                await self.send_group_help(command)
            else:
                await self.send_command_help(command)
            return None
        return super().command_not_found(string)

    async def send_error_message(self, error):
        if error is not None:
            await super().send_error_message(error)

    async def prepare_help_command(self, ctx, command):
        self._ref_command = command
        await super().prepare_help_command(ctx, command)


class MinimalNyxHelpCommand(MinimalHelpCommand):
    pass
