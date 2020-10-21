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

        filepath = "..\\DiscordBot\\resources\\images\\aoe2_online_stats.png"

        await ctx.send("In process. Might take a little. :)")
        aoe2_api = "https://aoe2.net/api/stats/players?game=aoe2de"

        data = ut.get_request_response(aoe2_api, json=True)
        logger.info(f"Requested player data from {aoe2_api}...")
        players = data["player_stats"][0]["num_players"]

        logger.info("Plotting of data has begun...")
        data_list = [players["steam"], players["multiplayer"], players["looking"], players["in_game"],
                     players["multiplayer_1h"], players["multiplayer_24h"]]
        # no legend, dark-ish color for all the bars - if each column should be a different color,
        # the data has to be prepared differently before plotting, in order to be able to access
        # the columns (bars) indivdually
        df = pd.DataFrame(data=data_list)
        ax = df.plot(kind="bar", legend=None, color="#333333")
        ax.set_title("AoE2:DE - current player stats -- powered by https://aoe2.net/#api",
                     fontweight="bold", x=0.5, y=1.075, bbox={"facecolor": "orange"})
        ax.set_xlabel("Status", x=0.02, y=0.8, style="italic", bbox={"facecolor": "orange"})
        ax.set_ylabel("Player numbers", x=1, y=0.05, style="italic", bbox={"facecolor": "orange"})
        ax = ut.set_bar_labels(ax=ax)  # set the bar labels for each bar
        xlabels = players.keys()  # the xlabels are the keys from the dict
        ax.set_xticklabels(xlabels, rotation=0, ha="center")
        figure = plt.gcf()
        figure.set_size_inches(19, 10)
        plt.savefig(filepath)
        logger.info(f"Saving plotted graph to {filepath}...")
        await ctx.send(file=discord.File(filepath))
      
    @commands.command(name="top",
                      help="Displays graph(s) of the Top players of the AoE2:DE leaderboard of your choosing."
                           "\nSimply enter the number of players you want to see (Defaults to 5 if left empty) "
                           "and the leaderboard ID (1v1 DM - 1, Team DM - 2, 1v1 RM - 3, Team RM - 4)! Defaults to 3."
                           "\nExample usage:"
                           "\n- !top 10 3"
                           "\nGets you the Top 10 players of the 1v1 RM leaderboard.")
    async def top(self, ctx, amount: int = 5, leaderboard_id: int = 3):
        """
        Command:\n
        Displays graph(s) for the top players of the current AoE2:DE leaderboard - data powered by aoe2.net/#api.
        For each 5 players, a new graph will be plotted.
        At the end, all graphs will be merged into one image vertically (horizontally is nice too)
        - with the help of a already pre-defined function which merges X number of images.

        After plotting the graphs and sending the merged image, all the used images will be swiftly deleted.

        Might put the separate parts of the function into their own function parts.

        :param ctx: the Context data (gets it from Discord)
        :param amount: the amount of players to get from the leaderboard - defaults to the first 5 players
                    (not more than 10000 allowed by the API)
        :param leaderboard_id: the leaderboard to get the top players from - defaults to the 1v1 RM leaderboard (ID: 3)

        :return: sends the plotted graph
        """

        # Leaderboard ID (Unranked=0, 1v1 Deathmatch=1, Team Deathmatch=2, 1v1 Random Map=3, Team Random Map=4)
        leaderboards_ids = {1: "1v1 Deathmatch", 2: "Team Deathmatch", 3: "1v1 Random Map", 4: "Team Random Map"}

        if amount > 10000:
            logger.debug(f"Entries to get ('{amount}') cannot be more than 10000!")
            return await ctx.send(f"The amount of players to get ('{amount}') cannot exceed 10000!")
        if leaderboard_id not in leaderboards_ids.keys():
            logger.debug(f"'{leaderboard_id}' is not a valid leaderboard ID.")
            return await ctx.send("Not a valid leaderboard ID. Available IDs:"
                                  "\n1v1 DM - 1, Team DM - 2, 1v1 RM - 3, Team RM - 4")

        leaderboard = leaderboards_ids[leaderboard_id]

        await ctx.send("Depending on how many players you requested, "
                       "it might take a little while to plot the graphs. "
                       "Please have a little bit of patience, thanks!")
        url = f"https://aoe2.net/api/leaderboard?game=aoe2de&leaderboard_id={leaderboard_id}&start=1&count={amount}"
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
            ax.set_title(f"Age Of Empires 2: Definitive Edition - Top Players (Leaderboard) {leaderboard}",
                         fontweight="bold", x=0.5, y=1.075, bbox={"facecolor": "orange"})
            # to set the legend to the place of your choosing
            # in my case outside the plot/box area
            ax.legend(bbox_to_anchor=(1, 1), loc="upper left")
            
            # to set the bar label for each bar in the chart with the actual value of the bar
            ax = ut.set_bar_labels(ax=ax)

            # retrieve x labels (names of the players) and current rank in the leaderboard and set them for each x label
            x_labels = []
            for idx, player in enumerate(chunk):
                player = str(chunk[idx]["rank"]) + " - " + chunk[idx]["name"]
                x_labels.append(player)

            # for the rotating of the x labels to horizontal and centering them
            ax.set_xticklabels(x_labels, rotation=0, ha="center")
            
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

        if amount > 5:  # since only 5 players per plot, merge them here together before sending
            merged_file = ut.merge_images(files_to_merge, file_name=f"top_{amount}_players")
            await ctx.send(f"Requested data of the Top {amount} players "
                           f"of the current AoE2:DE {leaderboard} leaderboard:",
                           file=discord.File(merged_file))
            # deleting all the image files with the naming scheme given - if none is found/deleted, nothing will happen
            ut.del_image_files(directory="..\\DiscordBot\\resources\\images\\", patterns=("top_*.png", "top_*.jpg"))
        else:  # if <= 5, simply only send the 1 plot
            await ctx.send(f"Requested data of the Top {amount} players "
                           f"of the current AoE2:DE {leaderboard} leaderboard:",
                           file=discord.File(filepath))
            # deleting all the image files with the naming scheme given - if none is found/deleted, nothing will happen
            ut.del_image_files(directory="..\\DiscordBot\\resources\\images\\", patterns=("top_*.png", "top_*.jpg"))
            
    @commands.command(name="rank",
                      help="Retrieves the current player/rank information for a given player. "
                           "If the player name has been omitted, the last successful retrieved data will be returned, "
                           "if available."
                           "\nNote: enter the name of the player as precise as it can get!")
    async def get_player_stats(self, ctx, player_name: str = ""):
        """
        Command:\n
        Retrieves the current rank and game stats of the given player.
        If the player name has been left empty, the last successful retrieved data, if available, will be returned.

        :param ctx: the Context data (gets it from Discord)
        :param player_name: the player to look for - defaults to nothing if left empty

        :return: returns the retrieved player information
        """

        # since the steam_id is empty: if no name is entered, the #1 player will be returned by default, after testing
        url = f"https://aoe2.net/api/nightbot/rank?leaderboard_id=3&" \
              f"search={player_name}&steam_id=&flag=false"  # name has to be as precise as it can get!
        logger.info(f"Retrieving player/rank data for '{player_name}' using '{url}...'")
        data = ut.get_request_response(link=url, json=False)
        logger.info(f"Retrieved the following data for player '{player_name}': '{data.text}'...")
        await ctx.send(data.text)
