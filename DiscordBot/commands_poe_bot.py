""" PoE (Path of Exile) SPECIFIC COMMANDS

Copyright © 2020 https://github.com/sixP-NaraKa - and all that shit.
Testing the Discord Bot functions and stuff.
"""

import requests
import re

import discord
from discord.ext import commands
import pandas as pd
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import bs4


# two dictionaries of the PoE currency items (in poe.trade)
# with the same entries but in a different "order" - nice to have, so you can look up items and
# their IDs both ways

# a dict: key = ID, value = name
currency_dict = {1: "Orb of Alteration", 2: "Orb of Fusing", 3: "Orb of Alchemy", 4: "Chaos Orb", 5: "Gemcutter's Prism",
                 6: "Exalted Orb", 7: "Chromatic Orb", 8: "Jeweller's Orb", 9: "Orb of Chance",
                 10: "Cartographer's Chisel", 11: "Orb of Scouring", 13: "Orb of Regret", 14: "Regal Orb",
                 15: "Divine Orb", 16: "Vaal Orb"}

# same as above, but order different: key = name, value = ID
currencies = {"Orb of Alteration": 1, "Orb of Fusing": 2, "Orb of Alchemy": 3, "Chaos Orb": 4, "Gemcutter's Prism": 5,
              "Exalted Orb": 6, "Chromatic Orb": 7, "Jeweller's Orb": 8, "Orb of Chance": 9, "Cartographer's Chisel": 10,
              "Orb of Scouring": 11, "Orb of Regret": 13, "Regal Orb": 14, "Divine Orb": 15, "Vaal Orb": 16}


def get_price(item_name, comp_item_name="Chaos Orb"):  # 2. item_id=6, 3. comp_item_id=4
    """ General method for searching for the price of a given Currency item in Path of Exile.

        This method is easily reusable and makes it easier to search for specific currency items.

        Once it has its items and the sum of them, it performs a median calculation, to find the "more correct" pricing
        than just the first item could bring (might be a bot/troll pricing it way lower, etc.).

        Instead of using the dict(s), you could also only take the ID's, though then you would have to memorize them.
        Then you could take the names during the parsing process.
        Also you could use the search function on the site via selenium, though this might take longer (performance).
        I think I am happy as it is. Will expand the dict with all the rest of the currency items -
        at least the basic ones soon-ish. ;)

        Uses the bs4 module for faster extracting (instead of selenium).

        :param item_name: the name of the item to look for (just for better output) - can also be parsed from the page
        :param comp_item_name: the item name to compare/price against (usually ID 4, i.e. Chaos Orb)

        :return: returns the extracted information
    """

    # if given currency name is NOT in the above dict, return
    if item_name not in currencies.keys() or comp_item_name not in currencies.keys():
        return f"This currency item does not exist, please try again."

    # if given currency name is in the above dict, continue here

    # set the item id and the compare item id to the value of their item names
    item_id = currencies[item_name]
    comp_item_id = currencies[comp_item_name]

    # if both lookup item and compare item are Chaos, set the compare item to Exalts
    if item_id == 4 and comp_item_id == 4:
        comp_item_id = 6

    currency_url = f"https://currency.poe.trade/search?league=Heist&online=x&stock=&want={item_id}&have={comp_item_id}"
    site = requests.get(currency_url)
    poetrade = bs4.BeautifulSoup(site.text, "html.parser")

    # get 5 listings and their pricing, so in order to get a better accurate pricing schema
    item_one = poetrade.select_one("div.displayoffer:nth-child(4) > div:nth-child(1) "
                                   "> div:nth-child(1) > small:nth-child(1)")
    item_two = poetrade.select_one("div.displayoffer:nth-child(5) > div:nth-child(1) "
                                   "> div:nth-child(1) > small:nth-child(1)")
    item_three = poetrade.select_one("div.displayoffer:nth-child(6) > div:nth-child(1) "
                                     "> div:nth-child(1) > small:nth-child(1)")
    item_four = poetrade.select_one("div.displayoffer:nth-child(7) > div:nth-child(1) "
                                    "> div:nth-child(1) > small:nth-child(1)")
    item_five = poetrade.select_one("div.displayoffer:nth-child(8) > div:nth-child(1) "
                                    "> div:nth-child(1) > small:nth-child(1)")

    items = [item_one.text, item_two.text, item_three.text, item_four.text, item_five.text]
    matches = []

    # https://stackoverflow.com/questions/4289331/how-to-extract-numbers-from-a-string-in-python/61134895#61134895
    # ^ Credit to this person for the following small section
    # pattern = "[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+"
    pattern = "[\d]*[.][\d]+|[\d]+"  # "|" to separate multiple patterns
    joined_items = "   ".join(items)
    if re.search(pattern, joined_items) is not None:
        for catch in re.finditer(pattern, joined_items):
            # print(catch[0])  # catch is a match object
            matches.append(catch[0])
            # it still catches the single "1"'s there, but not sure how to completely avoid that :/
            # will just write each catch[0] into a list, and then simply take every 2nd entry in that list LUL

    matches = matches[1::2]

    # iterate over the entries in the list and add them together
    sum_prices = float(0)
    for num in matches:
        sum_prices += float(num)

    # get the median (rough current price)
    result = sum_prices / len(matches)

    # get the compare item name via its ID - not really needed anymore, since we have it above already, but whatever
    comp_item_name = currency_dict[comp_item_id]
    return "One '{}' is worth roughly {:.4f} {}s. 10 roughly {:.4f}. \nURL: {}".format(item_name,
                                                                                       result,
                                                                                       comp_item_name,
                                                                                       result * 10,
                                                                                       currency_url)


class PoE(discord.ext.commands.Cog):
    """ PoE (Path of Exile) specific commands """

    @commands.command(name="price",
                      help="Returns back the current rough price of a given currency (in Chaos by default)."
                           "\nOnly the currency name is needed, optional comparison item name can be passed too "
                           "(but not needed). Defaults to comparison against: Chaos Orb."
                           "\nNote: names are case sensitive!")
    async def get_curr_price(self, ctx, currency_name, comparison_item_name="Chaos Orb"):
        """
        Command:\n
        Looks up the given currency name and its price compared to another currency (usually Chaos Orb).
        Uses the function :get_price(): for the main logic.

        :param ctx: the Context data (gets it from Discord)
        :param currency_name: the currency to search for
        :param comparison_item_name: optional - the name of the currency to make the comparison against
        (defaults to Chaos Orb if left empty)

        :return: sends the extracted information to the channel it was called from
        """
        
        price_info = get_price(item_name=currency_name, comp_item_name=comparison_item_name)
        await ctx.send(f"{price_info}")

    @commands.command(name="exalt",
                      help="Returns back the current rough price of an Exalted Orb."
                      "\nUse the !price command for other currencies.")
    async def get_price_exalt(self, ctx):
        """
        Command:\n
        Returns the price of the Exalted Orb only (compared to Chaos Orb).

        For other currencies, use the :get_curr_price(): command function.

        :param ctx: the Context data (gets it from Discord)

        :return: sends the extracted information to the channel it was called from
        """
      
        item_name = "Exalted Orb"
        # item_id = 6  # Exalt ID in poe.trade
        price_info = get_price(item_name=item_name)  # 2. item_id=item_id,
        await ctx.send(f"{price_info}")

    @commands.command(name="chaos",
                      help="Returns back the current rough price of an Chaos Orb."
                      "\nUse the !price command for other currencies.")
    async def get_price_chaos(self, ctx):
        """
        Command:\n
        Returns the price of the Chaos Orb only (compared to Exalted Orb).

        For other currencies, use the :get_curr_price(): command function.

        :param ctx: the Context data (gets it from Discord)

        :return: sends the extracted information to the channel it was called from
        """
        
        item_name = "Chaos Orb"
        # item_id = 4  # Chaos ID in poe.trade
        # comp_item_id = 6  # Exalt ID in poe.trade
        price_info = get_price(item_name=item_name)  # 2. item_id=item_id, 3. comp_item_id=comp_item_id
        await ctx.send(f"{price_info}")
