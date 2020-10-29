""" MISC COMMANDS """


from random import randint

import discord
from discord.ext import commands
import logging

import utils.utilities as ut
# from utils.utilities import send_file_dm


logger = logging.getLogger("discord.Misc")


class Misc(commands.Cog):
    """ Miscellaneous commands """

    def __init__(self, bot):  # bot is from --> discord_bot.CommandBot
        self.bot = bot
        logger.info("Misc() started...")

    @commands.command(pass_context=True,
                      name="madeby",
                      help="Outputs the creator of this Bot, as well as how to reach them if needed.",
                      ignore_extra=True)
    async def made_by(self, ctx):
        """
        Command:\n
        A bot command which gives out who made this Bot and how to reach them if necessary.

        :param ctx: the Context data (gets it from Discord)

        :return: the information who made this Bot
        """

        logger.info("!madeby command has been started and executed...")
        bot_info = await ctx.bot.application_info()
        embed = await ut.embed_message(title="Creator info",
                                       desc=f"This Bot has been made by {bot_info.owner.mention}."
                                       f"\nFor help, general feedback as well as feature requests "
                                       f"please contact {bot_info.owner.mention} "
                                       f"via a DM (direct message), or "
                                       f"visit the github page at: https://github.com/sixP-NaraKa/DiscordBot "
                                       f"and issue a request or even contribute yourself!"
                                       f"\nThank you!")
        await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(name="logs")
    @commands.guild_only()
    @commands.has_role("owner")
    async def get_log(self, ctx):
        """
        Command:\n
        Fetches the log fom this session and send it via a DM to the user who called this command.
        Only user with the "owner" role can use this command.

        :param ctx: the Context data (gets it from Discord)

        :return: the log file
        """

        logger.info(f"Sending the logs to {ctx.author}...")
        return await ut.send_file_dm(ctx.author, ctx.guild, ctx.channel.category, ctx.channel, ctx.command,
                                     text="Here is the requested log file.",
                                     info="",
                                     file=discord.File("logs\\bot_logs.log"))
