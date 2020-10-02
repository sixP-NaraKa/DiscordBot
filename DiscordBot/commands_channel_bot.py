""" CHANNEL/SERVER RELATED COMMANDS

Copyright © 2020 https://github.com/sixP-NaraKa - and all that shit.
Testing the Discord Bot functions and stuff.
"""


import discord
from discord.ext import commands

# where the other file(s) are located at to import from
from API.DiscordBot.standard_functions_bot import send_dm


class ChannelServer(discord.ext.commands.Cog):
    """ Channel and Guild/Server related commands """

    @commands.command(name="create-category",
                      help="Create a given category."
                           "\nOnly Users with the Admin role can use this command."
                           "\nSpaces, upper/lower case, as well as - & _ are allowed by Discord."
                           """\nIf you want to use spaces in the name, wrap the category name inside ' ' or " ".""",
                      ignore_extra=True)
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

        guild = ctx.guild
        existing_category = discord.utils.get(guild.categories, name=category_name)
        if existing_category is None:
            category = await guild.create_category_channel(category_name)
            return await ctx.send(f"Category {category} created!")
        else:
            return ctx.send(f"Category {category_name} already exists!")

    @commands.command(name="delete-category",
                      help="Deletes a given category. You can specify with <delete_channels> True to also"
                           "delete all its channels. Defaults to False if left empty."
                           "\nOnly Users with the Admin role can use this command."
                           "\nNote: case sensitive!",
                      ignore_extra=True)
    async def delete_category(self, ctx, category_name, delete_channels=False):
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

    @commands.command(name="create-channel",
                      help="Creates a channel (text or audio) - use simply t for Text, v for Voice."
                           "\nSince Discord doesn't allow capital names of TextChannels, "
                           "there is not much to be done about it... VoiceChannels work fine though lul."
                           "\nIf you want the channel to be created under a specific category, "
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
    async def create_channel(self, ctx, channel_name, text_or_voice, category_name=""):
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
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        # True or False, checked ob channel gibt

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

    @commands.command(name="members",
                      help="Outputs a list of all the current members of this guild."
                      "\nDiscrim = False if the Members should not have their #.... added. "
                           "Defaults to True if left empty."
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
    async def get_members(self, ctx, discrim=True):
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

        general_info = f"General information:" \
                       f"\n{ctx.bot.user.name} is connected to the following guild/server:" \
                       f"\nName - {ctx.guild}" \
                       f"\nID - {ctx.guild.id}" \
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
        await send_dm(user=user, guild=guild, channel=channel, command=triggered_command, text=members,
                      info=general_info)
        return await ctx.send(f"Sent you (@{user}) a DM containing more detailed information. :smiley:")
