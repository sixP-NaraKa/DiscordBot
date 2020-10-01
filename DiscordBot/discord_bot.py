# discord_bot.py

"""
Copyright © 2020 https://github.com/sixP-NaraKa - and all that shit.
Testing the Discord Bot functions and stuff.
"""

import os
from random import randint, choice
import requests

import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
import pandas as pd
import matplotlib.pyplot as plt


# ToDo:
#   - also, if desired by the user, delete all the channels (if applicable) from the specific category as well
#   - put the plotting in the online command maybe in a seperate function, for visibility sake
#       - also make it more pleasing looking
#       - also make the online command only usable in AoE channels/categories
#   - with the new functions and adding the older ones, keep up the documentation, etc.
#   - ...
#   - if you want to create category or channel the name of an already existing category or channel is crucial
#       - including wanting a channel which has the same name as a category and vice versa (i.e. it doesn't work then, cause already exists)
#       - might want to note that down in the commands / error messages to the user, etc.


load_dotenv("..\\DiscordBot\\.env.txt")
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!")

logging.basicConfig(level=logging.INFO)


""" HERE START THE GENERAL METHODS/FUNCTIONS """


async def send_dm(user, guild, channel, command, text, info=""):
    """
    A method to send a user whatever text this method has received.

    :param user: the message receiving user
    :param guild: the guild in which the Bot command call has been made from
    :param channel: the channel in which the command has been called in
    :param command: the command which triggered sending this DM (direct message)
    :param text: what text to send the user via a DM (direct message)
    :param info: optional additional information, which the user might find useful

    :return: nothing needs to be returned
    """

    await user.create_dm()
    await user.dm_channel.send(f"This DM has been triggered by command '!{command}' "
                               f"from guild/server '{guild}' in channel '{channel}'.\n"
                               f"\n{info}\n"
                               f"\n{text}")


""" HERE START THE BOT EVENTS """


@bot.event
async def on_ready():
    """
    Event:\n
    The on_ready method. Doesn't need to to anything, honestly. Can be removed.
    Might be nice to have for some testing, etc..

    :return: a string, saying that the Bot has successfully connected to Discord
    """

    # info = await bot.application_info()
    # print(f"This Bot has been created by {info.owner}")
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


""" HERE START THE BOT COMMANDS """


@bot.command(name="madeby",
             help="Outputs the creator of this Bot, as well as how to reach them if needed.",
             ignore_extra=True)
async def made_by(ctx):
    """
    Command:\n
    A bot command which gives out who made this Bot and how to reach them if necessary.

    :param ctx: the Context data (gets it from Discord)

    :return: the information who made this Bot
    """

    bot_info = await bot.application_info()
    return await ctx.send(f"This Bot has been made by {bot_info.owner}."
                          f"\nFor help, general feedback as well as feature requests please contact {bot_info.owner} "
                          f"via a DM (direct message)! Thank you!")


@bot.command(name="members",
             help="Outputs a list of all the current members of this guild."
                  "\nDiscrim = False if the Members should not have their #.... added. Defaults to True if left empty."
                  "\nExample Usage:\n"
                  "1.) !members\n"
                  "- Member1#1234\n"
                  "- Member2#2134\n"
                  "- ...\n"
                  "2.) !members False\n"
                  "- Member1\n"
                  "- Member2\n"
                  "- ...",
             ignore_extra=False)
@commands.guild_only()
async def get_members(ctx, discrim=True):
    """
    Command:\n
    Gets the current members from the guild the command has been invoked from.
    <discrim> is a optional argument - can be used to also get the "handle" (#....) together with the member name.
    \nThis function calls the send_dm(...) function above, in order to send DMs.
    \n

    Example usage:\n
    1.) !members
        - Member1#1234
        - Member2#2134
        - ...

    2.) !members False
        - Member1
        - Member2
        - ...

    :param ctx: the Context data (gets it from Discord)
    :param discrim: the discriminator ("handle") of the user account, i.e. UserName#2345 (UserName#discrim)

    :return: a message to the user who invoked this command, stating that they received a DM from the Bot.
    """

    general_info = f"General information:"\
                   f"\n{bot.user.name} is connected to the following guild/server:"\
                   f"\nName - {ctx.guild}"\
                   f"\nID - {ctx.guild.id}"\
                   f"\nMembers - {ctx.guild.member_count}"

    # gets the names of the current guild members only
    members = "Member list: \n- "
    if not discrim:
        # getting a string (joining) of all the members of the guild, with the help of a little list comprehension
        members += "\n- ".join([member.name for member in ctx.guild.members])

    # getting the discriminator, i.e. the #...., and adding it to the output, i.e. the name
    else:
        guild_members = []
        for member in ctx.guild.members:
            # appending the result of a joined list containing the user name and their discriminator
            guild_members.append("#".join([member.name, member.discriminator]))

        # joins the above extracted list of user name and discrim into an easy to output string
        members += "\n- ".join(guild_members)

    # can do only one return, since in this case here it works just fine
    user = ctx.author
    guild = ctx.guild
    channel = ctx.channel
    triggered_command = ctx.command
    await send_dm(user=user, guild=guild, channel=channel, command=triggered_command, text=members, info=general_info)
    return await ctx.send(f"Sent you (@{user}) a DM containing more detailed information. :smiley:")


@bot.command(name="roll",
             help="Rolls a dice with how many sides of your choosing. Defaults to 6 if <= 0.",
             ignore_extra=True)
async def roll_dice(ctx, number_of_sides="0"):
    """
    Command:\n
    A little game which rolls a dice given the amount of sides the user chose.

    :param ctx: the Context data (gets it from Discord)
    :param number_of_sides: optional parameter, user can choose how many sides the die should have.
        Defaults to 6 if empty, if 0 or a string representation of a number or else has been used.

    :return: the randomly chosen rolled number in range of 1 to param: number_of_sides
    """

    default = 5
    try:
        number_of_sides = int(number_of_sides)

        if number_of_sides <= 0:
            number_of_sides = default
            await ctx.send(f"Cannot be <= 0. Defaulted to 6.")

        dice = randint(1, number_of_sides + 1)
        # return await ctx.send(dice)
        return await ctx.send(f"Rolled: {dice}")

    except ValueError:
        return await ctx.send(f"Error: Cannot convert {number_of_sides} to an Integer. Only use whole numbers!")


@bot.command(name="ripit",
             help="♂ Do you like what you see? ♂",
             ignore_extra=True)
async def rip_it(ctx):
    """
    Command:\n
    Sends a gif.

    :param ctx: the Context data (gets it from Discord)

    :return: the gif
    """
    # user = ctx.author
    return await ctx.send(file=discord.File("C:\\Users\\IEUser\\Pictures\\external-content.duckduckgo.com.gif"))


@bot.command(name="create-category",
             help="Create a given category."
                  "\nOnly Users with the Admin role can use this command."
                  "\nSpaces, upper/lower case, as well as - & _ are allowed by Discord."
                  "\nIf you want to use spaces in the name, wrap the category name inside ' ' or " ".",
             ignore_extra=True)
@commands.has_role("admins")
async def create_category(ctx, category_name):
    """
    Command:\n
    Creates a given category.
    \nOnly Admins can use this command.

    :param ctx: the Context data (gets it from Discord)
    :param category_name: the name the category should have, defined by the user
    :return:
    """

    guild = ctx.guild
    existing_category = discord.utils.get(guild.categories, name=category_name)
    if existing_category is None:
        category = await guild.create_category_channel(category_name)
        return await ctx.send(f"Category {category} created!")
    else:
        return ctx.send(f"Category {category_name} already exists!")


@bot.command(name="delete-category",
             help="Deletes a given category. You can specify with <delete_channels> True to also"
                  "delete all its channels. Defaults to False if left empty."
                  "\nOnly Users with the Admin role can use this command."
                  "\nNote: case sensitive!",
             ignore_extra=True)
async def delete_category(ctx, category_name, delete_channels=False):
    """
    Command:\n
    Deletes a given category.
    ToDo: Optionally, all its channels as well.

    :param ctx: the Context data (gets it from Discord)
    :param category_name: the name of the category which the user wants to delete
    :param delete_channels: delete the channels as well - defaults to False if left empty

    :return: notifies the user of the outcome - if deleted or not
    """

    guild = ctx.guild
    existing_category = discord.utils.get(guild.categories, name=category_name)
    if existing_category is not None:
        # print(existing_category.channels)
        await ctx.send(f"Deleting category {category_name}."
                       f" Its channels (if applicable) have been moved to no category."
                       f" If you wish to delete them as well, use the !help <delete-channel> command.")
        await existing_category.delete()
        return await ctx.send(f"Category {category_name} deleted.")
    else:
        return await ctx.send(f"Cannot delete category {category_name}: does not exist. ")


@bot.command(name="create-channel",
             help="Creates a channel (text or audio) - use simply t for Text, v for Voice."
                  "\nSince Discord doesn't allow capital names of TextChannels, "
                  "there is not much to be done about it... VoiceChannels work fine though lul."
                  "\nIf you want the channel to be created under a specific category, simply add the name of the"
                  "category to the command. Note: case sensitive!"
                  "\nOnly Users with the Admin role can use this command."
                  "\nExample Usage:\n"
                  "1.) !create-channel MyChannelName t <optional category>\n"
                  "- text channel 'MyChannelName' has been created.\n"
                  "2.) !create-channel MyChannelName s <optional category>\n"
                  "- voice channel 'MyChannelName' has been created.",
             ignore_extra=False)
@commands.guild_only()
@commands.has_role("admins")
async def create_channel(ctx, channel_name, text_or_voice, category_name=""):
    """
    Command:\n
    Creates a text or voice based channel in a, if desired, given category.
    Returns an error when the channel already exists.
    \nOnly Users with the Admin role can use this command!
    \n

    Example Usage:\n
    1.) !create-channel MyChannelName t <optional category>
        - text channel "MyChannelName" has been created.

    2.) !create-channel MyChannelName s <optional category>
        - voice channel "MyChannelName" has been created.

    :param ctx: the Context data (gets it from Discord)
    :param channel_name: how the channel should be called
    :param text_or_voice: text or voice channel, t for text, v for voice
    :param category_name: optional - the category, if desired, in which the channel should be created under

    :return: creates the channel and notifies the user
    """

    guild = ctx.guild  # current guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)  # True or False, checked ob channel gibt

    # if the category name is not an empty string, look for that category
    if category_name != "":
        existing_category = discord.utils.get(guild.categories, name=category_name)
        # if the category does not exist, notify the user and discontinue
        if existing_category is None:
            return await ctx.send(f"Category {category_name} does not exist!")

    # if above category does exist, continue with the creation of the channel
    if not existing_channel:  # wert is da, also nicht null --> nicht empty also True, empty ist gleich False (etc.)
        await ctx.send(f"Trying to create new channel: {channel_name}")
        if text_or_voice == "t":
            if category_name != "":
                await guild.create_text_channel(channel_name, category=existing_category)
                return await ctx.send(f"Text channel {channel_name} created under category {category_name}.")
            else:
                await guild.create_text_channel(channel_name)
                return await ctx.send(f"Text channel {channel_name} created.")
        elif text_or_voice == "v":
            if category_name != "":
                await guild.create_voice_channel(channel_name, category=existing_category)
                return await ctx.send(f"Voice channel {channel_name} created under category {category_name}.")
            else:
                await guild.create_voice_channel(channel_name)
                return await ctx.send(f"Voice channel {channel_name} created.")
    else:
        return await ctx.send(f"{channel_name} channel already exists.")


@bot.command(name="delete-channel",
             help="Deletes a given channel. Note: Case sensitive."
                  "\nOnly Users with the Admin role can use this command."
                  "\nExample Usage:\n"
                  "1.) !delete-channel MyChannelName\n"
                  "- if channel exists, channel deleted",
             ignore_extra=False)
@commands.guild_only()
@commands.has_role("admins")
async def delete_channel(ctx, channel_name):
    """
    Command:\n
    Deletes a given channel. Returns an error message if the channel could not be found.
    \nOnly Users with the Admin role can use this command!
    \nNote: channel names are case-sensitive! Has been left untouched, because important!
    \n

    Example Usage:\n
    1.) !delete-channel MyChannelName
        - if channel exists, channel deleted

    :param ctx: the Context data (gets it from Discord)
    :param channel_name: the name of the channel which will be deleted

    :return: deletes the channel (if it exists) and notifies the user
    """

    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    # print(type(existing_channel))
    if existing_channel:
        # existing_channel_id = existing_channel.id
        await ctx.send(f"Deleting channel: {channel_name}")
        await existing_channel.delete()  # you need to call ON the channel itself the delete() method
        return await ctx.send(f"Channel {channel_name} deleted.")
    else:
        return await ctx.send(f"Cannot delete channel {channel_name}: does not exist.")


""" HERE START THE CHANNEL SPECIFIC COMMANDS """


@bot.command(name="online",
             help="Fetches the current amount of players in-game in AoE2:DE."
                  "\nThis command only works within Age Of Empires 2 channels!",
             ignore_extra=False)
@commands.guild_only()
async def get_online_players(ctx):
    """
    Command:\n
    Fetches the current amount of players in-game in AoE2.DE.
    \nThis command only works within Age Of Empires 2 channels!
    ToDo: make only usable in AoE specific categories - should be easier and better anyway.

    :param ctx: the Context data (gets it from Discord)

    :return: the current online player stats of AoE2:DE
    """

    filepath = "C:\\Users\\IEUser\\Pictures\\aoe.png"

    await ctx.send("In process. Might take a little. :)")
    aoe2_api = "https://aoe2.net/api/stats/players?game=aoe2de"
    response = requests.get(aoe2_api)
    data = response.json()
    players = data["player_stats"][0]["num_players"]

    # series = pd.Series(players).to_string()
    # await ctx.send(f"Here are the current player stats for Age Of Empires 2: Definitive Edition: "
    #                f"powered by https://aoe2.net/api"
    #                f"\n{series}")

    # here the plotting takes place, really rudimentary just for testing purposes
    data_list = [players["steam"], players["multiplayer"], players["looking"], players["in_game"],
                 players["multiplayer_1h"], players["multiplayer_24h"]]
    df = pd.DataFrame(data=data_list)
    ax = df.plot(kind="bar")
    ax.set_title("AoE2:DE - current player stats -- powered by https://aoe2.net/api")
    ax.set_xlabel("Status")
    ax.set_ylabel("Player numbers")
    xlabels = players.keys()  # the xlabels are the keys from the dict
    ax.set_xticklabels(xlabels, rotation=0, ha="center")
    # ax.legend(visible=False)
    figure = plt.gcf()
    figure.set_size_inches(19, 10)
    plt.savefig(filepath)
    await ctx.send(file=discord.File(filepath))


@bot.command(name="cat",
             help="Get the current category you are in. None if in no category.")
@commands.guild_only()
async def get_current_category(ctx):
    """
    Command:\n
    Get the current category you are in. None if in no category.

    :param ctx: the Context data (gets it from Discord)

    :return: the category where the command has been called from
    """

    category = ctx.channel.category
    # print(category)

    if category is not None:
        channels_cat = category.channels
        # print(channels_cat)
        channel_names = ""
        for channel in channels_cat:
            channel_names += channel.name + "\n"

        # return await ctx.send(f"You are in category: {category}."
        #                       f"\nThe category has the following channels: {channel_names}")

        await send_dm(ctx.author, ctx.guild, ctx.channel, ctx.command, channel_names)
        return await ctx.send(f"Sent you (@{ctx.author}) a DM containing more detailed information. :smiley:")
    else:
        return await ctx.send("You are in no category.")


bot.run(TOKEN)
