""" Main class/file.

The corresponding commands have been moved to different files and their classes.
Easier time to manage the code.

See:
- cogs.server
- cogs.misc
- cogs.aoe
- cogs.poe
- utils.utilities
"""


import os

from discord.ext import commands
from dotenv import load_dotenv
import logging

# where the other file(s) are located at to import from
from cogs.server import Server
from cogs.misc import Misc
from cogs.aoe import AoE
from cogs.poe import PoE


""" BOT CLASS WITH EVENTS """


class CommandBot(commands.Bot):  # inherit from discord.ext.commands.Bot
    """ The CommandBot - including events """

    def __init__(self):
        super().__init__(command_prefix="!")
        # self.bot = commands.Bot(command_prefix="!")
        self.on_ready = self.event(self.on_ready)
        self.on_member_join = self.event(self.on_member_join)
        self.on_command_error = self.event(self.on_command_error)

    def startup(self, bot_token):
        """
        Adds the Cogs to the Bot and starts said Bot.

        :param bot_token: the Token with which the Bot should ultimately log in as
        """

        # adding the Cogs to the Bot
        # "self" --> CommandBot (inherits from discord.ext.commands.Bot)
        # "bot" instead of "self" also works fine, in this case, because "bot = CommandBot()" when started
        self.add_cog(Server(bot=self))
        self.add_cog(Misc(bot=self))
        self.add_cog(AoE(bot=self))
        self.add_cog(PoE(bot=self))
        cogs = ", ".join(self.cogs.keys())
        logger.info(f"All Cogs '{cogs}' successfully loaded...")

        # starts the Bot with the given Bot Token
        self.run(bot_token)
        # self.loop.run_until_complete(self.run(bot_token))
        # self.loop.run_forever(self=self.run(bot_token))

    async def stop(self):
        """
        If the Bot should be stopped/closed, maybe after a certain event has happened (error, etc.).
        """

        return NotImplementedError

    async def load_cogs(self):
        """
        Loads the given Cogs one by one.
        So you can easily add more Cogs without too much effort.
        """

        return NotImplementedError

    async def on_ready(self):
        """
        Event:\n
        The on_ready method. Doesn't need to to anything, honestly. Can be removed.
        Might be nice to have for some testing, etc..

        :return: a string, saying that the Bot has successfully connected to Discord
        """

        logger.debug("Started.....")
        # ctx.bot. ... can also be used
        return f"{self.user.name} has connected to Discord!"

    async def on_command_error(self, ctx, error):
        """
        Event:\n
        Whenever a command error (specified below) happens, a error message will be thrown, notifying the user.
        \n
        # CheckFailure: not correct role/permissions\n
        MissingRole: missing a specific role to perform command\n
        MissingPermissions: ^\n
        CommandNotFound: command not found\n
        MissingRequiredArgument: one or more required arguments have not been passed to the command\n
        BadArgument: one or more arguments could not be converted to the required datatype\n
        TooManyArguments: if too many arguments have been passed, notify user\n\n
        NoPrivateMessage: if a command has been invoked from a private message (dm) and the command has the\n
        commands.guild_only() decorator parameter/tag, notify the user that the command does not work here\n

        :param ctx: the Context data (gets it from Discord)
        :param error: the error (gets it from Discord)

        :return: a message to the user, notifying them what happened
        """

        # if isinstance(error, commands.errors.CheckFailure):
        #     return await ctx.send("You do not have the correct role/permissions for this command.")
        if isinstance(error, commands.errors.MissingRole) or isinstance(error, commands.errors.MissingPermissions):
            logger.error(f"User {ctx.author}, with ID {ctx.author.id} is missing the needed roles "
                         f"to perform command '{ctx.message.content}': {error}...")
            return await ctx.send("You do not have the correct role/permissions for this command.\n"
                                  "Contact your guild/server Admins if you think this is incorrect.")
        if isinstance(error, commands.errors.CommandNotFound):
            logger.error(f"User {ctx.author}, with ID {ctx.author.id} tried to use a command '{ctx.message.content}'"
                         f", which does not exist: {error}..."
                         f"See below 'WebSocket Event' for full detail.")
            return await ctx.send("This command does not exist. Type !help to see all available commands.")
        if isinstance(error, commands.errors.MissingRequiredArgument):
            logger.error(f"User {ctx.author}, with ID {ctx.author.id} tried to use a command '{ctx.message.content}'"
                         f", but did not supply the required argument(s): {error}...")
            return await ctx.send("Error: One or more required arguments have not been passed through."
                                  "\nSee !help <command> for more information and example usages.")
        if isinstance(error, commands.errors.BadArgument):
            logger.error(f"User {ctx.author}, with ID {ctx.author.id} tried to use a command '{ctx.message.content}'"
                         f", with one or more bad arguments: {error}...")
            return await ctx.send("Error: One or more arguments could not be converted to the required type."
                                  "\nSee !help <command> for more information and example usages.")
        if isinstance(error, commands.errors.TooManyArguments):
            logger.error(f"User {ctx.author}, with ID {ctx.author.id} tried to use a command '{ctx.message.content}'"
                         f", with too many arguments: {error}...")
            return await ctx.send("Error: Too many arguments have been passed to the command."
                                  "\nSee !help <command> for more information and example usages."
                                  "\n\nIf you want this notification to not appear, contact the creator of this Bot.")
        if isinstance(error, commands.errors.NoPrivateMessage):  # the commands.guild_only() tag throws this error
            logger.error(f"User {ctx.author}, with ID {ctx.author.id} tried to use a command '{ctx.message.content}'"
                         f", which does not work in Private Messages: {error}...")
            return await ctx.send("Error: This command does not work in a private message.")
        # just print out any other exceptions to the console for now and log them
        else:
            print(error)
            logger.error(error)
            return await ctx.send(f"Something unexpected happened..."
                                  f"\nTry the command '{ctx.command}' again. "
                                  f"If the problem persists, contact an Admin/the creator of this Bot. Thank you!")


if __name__ == "__main__":
    # start the logger
    logger = logging.getLogger("discord")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename="logs\\bot_logs.log", encoding="UTF-8", mode="w")
    handler.setFormatter(logging.Formatter("%(asctime)s: %(levelname)-8s: %(name)-20s: "
                                           "%(lineno)-5d %(funcName)-20s: %(message)s"))
    logger.addHandler(handler)

    load_dotenv(dotenv_path=".env.env")
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN is None:
        logger.error("Bot Token cannot be None! .env file may be missing, 'cause dotenv doesn't error out, "
                     "even if you put verbose=True (always returns True, no matter what)..."
                     "Exiting...")
        raise RuntimeError("The Bot Token cannot be of NoneType! .env file may be missing, "
                           "'cause dotenv doesn't error out, even if you put verbose=True "
                           "(always returns True, no matter what)...")

    # start the Bot
    bot = CommandBot()
    bot.startup(TOKEN)
