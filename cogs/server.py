""" GUILD/SERVER RELATED COMMANDS """


import discord
from discord.ext import commands
import logging

import utils.utilities as ut
# from utils.utilities import send_dm


logger = logging.getLogger("discord.Server")


class Server(commands.Cog):
    """ Channel and Guild/Server related commands """

    def __init__(self, bot):  # bot is from --> discord_bot.CommandBot
        self.bot = bot
        logger.info("Server() started...")

    @commands.command(name="create-category",
                      help="Create a given category."
                           "\nOnly Users with the Admin role can use this command."
                           "\nSpaces, upper/lower case, as well as - & _ are allowed by Discord."
                           """\nIf you want to use spaces in the name, wrap the category name inside ' ' or " ".""",
                      ignore_extra=True)
    @commands.guild_only()
    @commands.has_role("admins")
    async def create_category(self, ctx, category_name):
        """
        Command:\n
        Creates a given category.
        \nOnly Admins can use this command.

        :param ctx: the Context data (gets it from Discord)
        :param category_name: the name the category should have, defined by the user
        :return:
        """

        logger.info(f"Creating new category '{category_name}'...")
        guild = ctx.guild
        existing_category = discord.utils.get(guild.categories, name=category_name)
        if existing_category is None:
            category = await guild.create_category_channel(category_name)
            logger.info(f"Category '{category_name}' created!")
            return await ctx.send(f"Category '{category}' created!")
        else:
            logger.debug(f"Category '{category_name}' already exists!")
            return ctx.send(f"Category '{category_name}' already exists!")

    @commands.command(name="delete-category",
                      help="Deletes a given category. You can specify with <delete_channels> True to also "
                           "delete all its channels. Defaults to False if left empty."
                           "\nOnly Users with the Admin role can use this command."
                           "\nNote: case sensitive!",
                      ignore_extra=True)
    @commands.guild_only()
    @commands.has_role("admins")
    async def delete_category(self, ctx, category_name: str, delete_channels: bool = False):
        """
        Command:\n
        Deletes a given category.
        Optionally, with delete_channels = True, all its channels as well. Defaults to False.

        :param ctx: the Context data (gets it from Discord)
        :param category_name: the name of the category which the user wants to delete
        :param delete_channels: delete the channels as well - defaults to False if not set to True

        :return: notifies the user of the outcome - if deleted or not
        """

        logger.info(f"Deleting category '{category_name}'...")
        existing_category = discord.utils.get(ctx.guild.categories, name=category_name)
        if existing_category is not None:  # if the category exists
            if delete_channels is True and existing_category.channels is not None:  # ... and if channels are not empty
                names = []
                for channel in existing_category.channels:
                    names.append(channel.name)
                    await channel.delete()
                response = "Deleted channels: \n" + "\n".join(names) + "\n"
            # after the channels have been deleted (or not), continue with the deletion of the category itself
            else:
                response = f"Category '{existing_category}' has no channels to delete. Skipping...\n"
                logger.info(f"Category {existing_category} has no channels to delete. Skipping...")

            await existing_category.delete()
            logger.info(f"Category '{existing_category}' deleted (and its channels if applicable)...")
            return await ctx.send(f"{response}"
                                  f"Category '{existing_category}' deleted.")
        else:
            logger.debug(f"Category '{category_name}' does not exist...")
            return await ctx.send(f"Cannot delete category '{category_name}': does not exist. ")

    @commands.command(name="create-channel",
                      help="Creates a channel (text or audio) - use simply t for Text, v for Voice."
                           "\nSince Discord doesn't allow capital names of TextChannels, "
                           "there is not much to be done about it... VoiceChannels work fine though."
                           "\nStill, no duplicate names (doesn't matter if upper/lower-case, etc.) allowed for now. :)"
                           "The same names are only allowed for each one voice and text based channel, but not more."
                           "For example: 'Test' voice and 'test' text can coexist together. "
                           "but not a second one of either."
                           "\n\nIf you want the channel to be created under a specific category, "
                           "simply add the name of the category to the command. Note: case sensitive!"
                           "\nOnly Users with the Admin role can use this command."
                           "\nExample Usage:\n"
                           "1.) !create-channel MyChannelName t <optional category>\n"
                           "- text channel 'MyChannelName' has been created.\n"
                           "2.) !create-channel MyChannelName s <optional category>\n"
                           "- voice channel 'MyChannelName' has been created.",
                      ignore_extra=False)
    @commands.guild_only()
    @commands.has_role("admins")
    async def create_channel(self, ctx, channel_name: str, text_or_voice: str, category_name: str = ""):
        """
        Command:\n
        Creates a text or voice based channel in a, if desired, given category.
        Returns an error when the channel already exists in the given category,
        otherwise it will create it under no category.
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

        logger.info(f"Creating channel '{channel_name}' under possible category '{category_name}'...")
        # simple check to see if the channel name .lower() already exists in the server/guild
        # only text based channels are always put to lower-case, no matter what
        # in order to, at this moment, make it easier to handle the deletion of individual channels,
        # use name=channel_name.lower()
        # not a good way to do it, but at least something for now, will change it in the future - maybe ;)
        existing_channel = discord.utils.get(ctx.guild.channels, name=channel_name.lower())
        existing_category = discord.utils.get(ctx.guild.categories, name=category_name)
        if existing_channel:  # if channel already exists (looks for it in the whole server/guild - for now), return
            logger.info(f"Channel '{channel_name}' already exists! Exiting...")
            return await ctx.send(f"Channel '{channel_name}' already exists.")
        if category_name != "" and not existing_category:  # if a category was specified and it does not exist
            logger.info(f"Category '{category_name}' does not exist! Exiting...")
            return await ctx.send(f"Category '{category_name}' does not exist.")

        # if the checks so far have been successful, see if text or voice channel should be created
        text_or_voice = text_or_voice.lower()
        if text_or_voice == "t" and existing_category:  # if "t" and specified category exists
            logger.info(f"Text channel '{channel_name}' created under category '{category_name}'.")
            await ctx.guild.create_text_channel(channel_name, category=existing_category)
            return await ctx.send(f"Text channel '{channel_name}' created under category '{category_name}'.")
        elif text_or_voice == "t" and category_name == "":  # if "t" only and category was unspecified
            logger.info(f"Text channel '{channel_name}' created.")
            await ctx.guild.create_text_channel(channel_name)
            return await ctx.send(f"Text channel '{channel_name}' created.")
        if text_or_voice == "v" and existing_category:  # if "v" and specified category exists
            logger.info(f"Voice channel '{channel_name}' created under category '{category_name}'.")
            await ctx.guild.create_voice_channel(channel_name, category=existing_category)
            return await ctx.send(f"Voice channel '{channel_name}' created under category '{category_name}'.")
        elif text_or_voice == "v" and category_name == "":  # if "v" only and category was unspecified
            logger.info(f"Voice channel '{channel_name}' created.")
            await ctx.guild.create_voice_channel(channel_name)
            return await ctx.send(f"Voice channel '{channel_name}' created.")
        else:  # if none of the above (neither "t" or "v" essentially)
            logger.debug("Neither 't' (for Text) or 'v' (for Voice) as the channel base have been specified!")
            return await ctx.send("Specify the channel to be created as either 't' (or 'T') for a text-based channel, "
                                  "or 'v' (or 'V') for a voice-based channel."
                                  "\nSee '!help create-channel' for example usages.")

    @commands.command(name="delete-channel",
                      help="Deletes a given channel. Note: Case sensitive."
                           "\nOnly Users with the Admin role can use this command."
                           "\nExample Usage:\n"
                           "1.) !delete-channel MyChannelName\n"
                           "- if channel exists, channel deleted",
                      ignore_extra=False)
    @commands.guild_only()
    @commands.has_role("admins")
    async def delete_channel(self, ctx, channel_name):
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

        logger.info(f"Deleting channel '{channel_name}'...")
        guild = ctx.guild
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if existing_channel:
            # existing_channel_id = existing_channel.id
            logger.info(f"Deleted channel '{channel_name}'...")
            await ctx.send(f"Deleting channel: '{channel_name}'")
            await existing_channel.delete()
            return await ctx.send(f"Channel '{channel_name}' deleted.")
        else:
            logger.info(f"Cannot delete channel '{channel_name}': does not exist...")
            return await ctx.send(f"Cannot delete channel '{channel_name}': does not exist.")
