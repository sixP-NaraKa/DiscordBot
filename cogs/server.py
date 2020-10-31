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
        
    @commands.command(hidden=True)  # hides the command from the !help window in discord
    @commands.guild_only()
    @commands.is_owner()
    async def setup_channels(self, ctx):
        """
        Command:\n
        Hidden server owner-only command which, as a setup, creates the channels "needed" for the Bot.
        Only Text-channels atm!

        The command will not notify about the creation of categories/channels, but will only log it.

        :param ctx: the Context data (gets it from Discord)
        """

        # categories and their channels (text channels only)
        # at the moment just some random channels, for testing purposes
        cats_chs = {
                    "Bot": ["bot-spam", "help", "tutorial", "suggestions"],
                    "AoE2": ["matchmaking", "discussions"],
                    "PoE": ["trade", "groups"],
                    }

        # async for guild in self.bot.fetch_guilds():
        for guild in self.bot.guilds:  # or ctx.bot.guilds
            created = []
            logger.info(f"Starting to create categories and their channels '{cats_chs}' for guild '{guild}'...")
            for category in cats_chs.keys():
                existing_category = discord.utils.get(guild.categories, name=category)
                if not existing_category:  # if the category does not exist
                    cat = await guild.create_category_channel(category)
                    created.append(category)
                else:
                    cat = existing_category
                for channel in cats_chs.get(category):
                    existing_channel = discord.utils.get(cat.channels, name=channel)
                    if not existing_channel:  # if the channel does not exist, else just don't do anything
                        await cat.create_text_channel(name=channel)
                        created.append(channel)
            logger.info(f"Created these categories/channels: {', '.join(created)}... "
                        f"The rest already existed, if applicable.")
