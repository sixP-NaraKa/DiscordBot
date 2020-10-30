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
