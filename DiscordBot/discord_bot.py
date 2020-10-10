# discord_bot.py

"""
Main class/file.
The corresponding commands have been moved to different files and their classes.
Easier time to manage the code.

See:
- .commands_server_bot
- .commands_misc_bot
- .commands_aoe_bot
- .commands_poe_bot
- .standard_functions_bot
"""


import os

from discord.ext import commands
from dotenv import load_dotenv
import logging

# where the other file(s) are located at to import from
from API.DiscordBot.commands_server_bot import Server
from API.DiscordBot.commands_misc_bot import Misc
from API.DiscordBot.commands_aoe_bot import AoE
from API.DiscordBot.commands_poe_bot import PoE


# pass_context=True: with the .commands maybe not even needed.
# Seems to work fine. :/ Hmm, maybe it doesn't do what I think it does

# start the logger at the start of the application - basic configuration (logs whatever can be logged, essentially)
# logging.basicConfig(filename="logs\\bot_logs.log", filemode="a", level=logging.DEBUG)
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="logs\\bot_logs.log", encoding="UTF-8", mode="w")  # "w" - resets every run
handler.setFormatter(logging.Formatter("%(asctime)s: %(levelname)s: %(name)s: %(message)s"))
logger.addHandler(handler)

load_dotenv("..\\DiscordBot\\.env.txt")
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!")

# adding the command categories as well as their commands
bot.add_cog(Server())
bot.add_cog(Misc())
bot.add_cog(AoE())
bot.add_cog(PoE())


""" BOT EVENTS """


@bot.event
async def on_ready():
    """
    Event:\n
    The on_ready method. Doesn't need to to anything, honestly. Can be removed.
    Might be nice to have for some testing, etc..

    :return: a string, saying that the Bot has successfully connected to Discord
    """

    # ctx.bot.... can also be used
    return f"{bot.user.name} has connected to Discord!"


@bot.event
async def on_member_join(member):
    """
    Event:\n
    Whenever a new member joins this guild/server, a welcome message will be automatically sent to the user.
    This can be used to give the new member some important information about the guild/server, etc..

    :param member: the member which joined

    :return: nothing needs to be returned
    """

    # sends a new user to the guild/server a DM (direct message)
    await member.create_dm()
    await member.dm_channel.send(f"Oy {member.name}! ;)")


@bot.event
async def on_command_error(ctx, error):
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
        return await ctx.send("You do not have the correct role/permissions for this command.\n"
                              "Contact your guild/server Admins if you think this is incorrect.")
    if isinstance(error, commands.errors.CommandNotFound):
        return await ctx.send("This command does not exist. Type !help to see all available commands.")
    if isinstance(error, commands.errors.MissingRequiredArgument):
        return await ctx.send("Error: One or more required arguments have not been passed through."
                              "\nSee !help <command> for more information and example usages.")
    if isinstance(error, commands.errors.BadArgument):
        return await ctx.send("Error: One or more arguments could not be converted to the required type."
                              "\nSee !help <command> for more information and example usages.")
    if isinstance(error, commands.errors.TooManyArguments):  # ignore_extra defaults to True if not set explicitly
        # might fuck things up if left to true, depending on the command potentially
        return await ctx.send("Error: Too many arguments have been passed to the command."
                              "\nSee !help <command> for more information and example usages."
                              "\n\nIf you want this notification to not appear, contact the creator of this Bot.")
    if isinstance(error, commands.errors.NoPrivateMessage):  # the commands.guild_only() tag throws this error
        return await ctx.send("Error: This command does not work in a private message.")


bot.run(TOKEN)
