""" AOE SPECIFIC COMMANDS

Copyright © 2020 https://github.com/sixP-NaraKa - and all that shit.
Testing the Discord Bot functions and stuff.
"""


import requests

import discord
from discord.ext import commands
import pandas as pd
import matplotlib.pyplot as plt


class AoE(discord.ext.commands.Cog):
    """ Age of Empires 2 specific commands """

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
