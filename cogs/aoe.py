""" AOE SPECIFIC COMMANDS """


import discord
from discord.ext import commands
import logging
import pandas as pd
import matplotlib.pyplot as plt

import utils.utilities as ut
# from utils.utilities import get_request_response


logger = logging.getLogger("discord.AoE")


class AoE(commands.Cog):
    """ Age of Empires 2 specific commands """

    def __init__(self, bot):  # bot is from --> discord_bot.CommandBot
        self.bot = bot
        logger.info("AoE() started...")

    @commands.command(name="online",
                      help="Fetches the current amount of players in-game in AoE2:DE."
                      "\nThis command only works within Age Of Empires 2 channels!",
                      ignore_extra=False)
    @commands.guild_only()
    async def get_online_players(self, ctx):
        """
        Command:\n
        Fetches the current amount of players in-game in AoE2.DE.
        \nThis command only works within Age Of Empires 2 channels!
        ToDo: make only usable in AoE specific categories - should be easier and better anyway.

        :param ctx: the Context data (gets it from Discord)

        :return: the current online player stats of AoE2:DE
        """

        filepath = "..\\DiscordBot\\resources\\images\\ao2_stats.png"

        await ctx.send("In process. Might take a little. :)")
        aoe2_api = "https://aoe2.net/api/stats/players?game=aoe2de"

        data = ut.get_request_response(aoe2_api, json=True)
        logger.info(f"Requested player data from {aoe2_api}...")
        players = data["player_stats"][0]["num_players"]

        # here the plotting takes place, really rudimentary just for testing purposes
        logger.info("Plotting of data has begun...")
        data_list = [players["steam"], players["multiplayer"], players["looking"], players["in_game"],
                     players["multiplayer_1h"], players["multiplayer_24h"]]
        df = pd.DataFrame(data=data_list)
        ax = df.plot(kind="bar")
        ax.set_title("AoE2:DE - current player stats -- powered by https://aoe2.net/api")
        ax.set_xlabel("Status")
        ax.set_ylabel("Player numbers")
        xlabels = players.keys()  # the xlabels are the keys from the dict
        ax.set_xticklabels(xlabels, rotation=0, ha="center")
        figure = plt.gcf()
        figure.set_size_inches(19, 10)
        plt.savefig(filepath)
        logger.info(f"Saving plotted graph to {filepath}...")
        await ctx.send(file=discord.File(filepath))
      
    @commands.command(name="top",
                      help="Displays graph(s) of the Top players in 1v1 RM of the AoE2: DE leaderboard."
                           "\nSimply enter the number of players you want to see! Defaults to 5 if left empty."
                           "\nExample usage:"
                           "\n- !top 10")
    async def top(self, ctx, amount: int = 5):
        """
        Command:\n
        Displays graph(s) for the top players of the current AoE2:DE leaderboard.
        For each 5 players, a new graph will be plotted.
        At the end, all graphs, will be merged into one image vertically - with the help of a already pre-defined
        function which merges X number of images.
        After plotting the graphs and sending the merged image, all the used images will be swiftly deleted.
        ToDo: make the command also usable with other AoE2:DE game modes, and not only 1v1 RM (should be pretty easy)

        Might put the separate parts of the function into their own function parts.

        :param ctx: the Context data (gets it from Discord)
        :param amount: the amount of players to get from the leaderboard - defaults to the first 5 players

        :return: sends the plotted graph
        """

        await ctx.send("Depending on how many players you requested, "
                       "it might take a little while to plot the graphs. "
                       "Please have a little bit of patience, thanks!")
        url = f"https://aoe2.net/api/leaderboard?game=aoe2de&leaderboard_id=3&start=1&count={amount}"
        data = ut.get_request_response(url, json=True)
        data = data["leaderboard"]

        # saving in here the filepaths of the possibly to be merged files
        # if the amount of players to extract is <= than 5, this list here will simply be ignored, as it is not needed
        files_to_merge = []

        # determines how many runs are needed to be completed with the given amount of players to get
        runs = float(amount) / float(5)

        start = 0
        end = 5
        from math import ceil
        # here the loop runs as long as there are still players to extract
        for _ in range(ceil(runs)):  # the math.ceil() method helps us rounding UP to the nearest integer

            # always takes the next up to 5 players from the remaining data
            chunk = data[start:end:1]

            df = pd.DataFrame(chunk)

            ax = df.plot(x="rank", y=["highest_rating", "rating", "games", "wins", "losses"], kind="bar")
            ax.set_xlabel("Player", x=0.02, y=0.8, style="italic", bbox={"facecolor": "orange"})
            ax.set_ylabel("Amount", x=1, y=0.05, style="italic", bbox={"facecolor": "orange"})
            ax.set_title("Age Of Empires 2: Definitive Edition - Top Players (Leaderboard) 1v1 RM",
                         fontweight="bold", x=0.5, y=1.075, bbox={"facecolor": "orange"})
            # to set the legend to the place of your choosing
            # in my case outside the plot/box area
            ax.legend(bbox_to_anchor=(1, 1), loc="upper left")

            # retrieve x labels (names of the players) and current rank in the leaderboard and set them for each x label
            x_labels = []
            for idx, player in enumerate(chunk):
                player = str(chunk[idx]["rank"]) + " - " + chunk[idx]["name"]
                x_labels.append(player)

            # for the rotating of the x labels to horizontal and centering them
            ax.set_xticklabels(x_labels, rotation=0, ha="center")

            # to set the bar label for each bar in the chart with the actual value of the bar
            for rect in ax.patches:
                y_value = rect.get_height()
                x_value = rect.get_x() + rect.get_width() / 2

                space = 3
                va = "bottom"

                if y_value < 0:  # take values <0 also into consideration
                    space *= -1
                    va = "top"

                label = "{:.0f}".format(y_value)
                ax.annotate(
                    label,
                    (x_value, y_value),
                    xytext=(0, space),
                    textcoords="offset points",
                    ha="center",
                    va=va,
                    rotation=45)

            # sets the current figure via gcf() to a size in inches,
            # so the graph can be saved in a higher resolution / bigger size (so it is more readable)
            figure = plt.gcf()
            figure.set_size_inches(19, 10)

            filepath = f"..\\DiscordBot\\resources\\images\\top_players_{_}.png"
            files_to_merge.append(filepath)
            # https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.savefig.html --> all the parameters usable
            plt.savefig(filepath, bbox_inches="tight")

            # continue with more data, if available
            end += 5
            start += 5

        if amount > 5:  # since only 5 players per plot, save them into a list to later merge them together
            merged_file = ut.merge_images(files_to_merge, file_name=f"top_{amount}_players")
            await ctx.send(f"Requested data of the Top {amount} players of the current AoE2:DE 1v1 RM leaderboard:",
                           file=discord.File(merged_file))
            # deleting all the image files with the naming scheme given - if none is found/deleted, nothing will happen
            ut.del_image_files(directory="..\\DiscordBot\\resources\\images\\", patterns=("top_*.png", "top_*.jpg"))
        else:  # if <= 5, simply only send the 1 plot
            await ctx.send(f"Requested data of the Top {amount} players of the current AoE2:DE 1v1 RM leaderboard:",
                           file=discord.File(filepath))
            # deleting all the image files with the naming scheme given - if none is found/deleted, nothing will happen
            ut.del_image_files(directory="..\\DiscordBot\\resources\\images\\", patterns=("top_*.png", "top_*.jpg"))
