""" MISC COMMANDS

Copyright © 2020 https://github.com/sixP-NaraKa - and all that shit.
Testing the Discord Bot functions and stuff.
"""


from random import randint

import discord
from discord.ext import commands

from .standard_functions_bot import send_image_dm


class Misc(commands.Cog):
    """ Miscellaneous commands """

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

        bot_info = await ctx.bot.application_info()
        return await ctx.send(f"This Bot has been made by {bot_info.owner}."
                              f"\nFor help, general feedback as well as feature requests "
                              f"please contact {bot_info.owner} "
                              f"via a DM (direct message)! Thank you!")

    @commands.command(name="roll",
                      help="Rolls a dice with how many sides of your choosing. Defaults to 6 if <= 0.",
                      ignore_extra=True)
    async def roll_dice(self, ctx, number_of_sides="0"):
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

    @commands.command(name="ripit",
                      help="♂ Do you like what you see? ♂",
                      ignore_extra=True)
    async def rip_it(self, ctx):
        """
        Command:\n
        Sends a gif.

        :param ctx: the Context data (gets it from Discord)

        :return: the gif
        """
        
        return await ctx.send(file=discord.File("..\\Screenshots\\external-content.duckduckgo.com.gif"))

    
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

        return await send_image_dm(ctx.author, ctx.guild, ctx.channel.category, ctx.channel, ctx.command,
                                   text="Here is the requested log file.",
                                   info="",
                                   file=discord.File("logs\\bot_logs.log"))
    
