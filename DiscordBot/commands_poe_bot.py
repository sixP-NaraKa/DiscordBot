""" PoE (Path of Exile) SPECIFIC COMMANDS

Copyright © 2020 https://github.com/sixP-NaraKa - and all that shit.
Testing the Discord Bot functions and stuff.
"""

import requests
import re
from time import sleep

import discord
from discord.ext import commands
import pandas as pd
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import bs4
import numpy as np
import PIL
from PIL import Image
from pyperclip import paste


# two dictionaries of the PoE currency items (in poe.trade)
# with the same entries but in a different "order" - nice to have, so you can look up items and
# their IDs both ways

# a dict: key = ID, value = name
currency_dict = {1: "Orb of Alteration", 2: "Orb of Fusing", 3: "Orb of Alchemy", 4: "Chaos Orb", 5: "Gemcutter's Prism",
                 6: "Exalted Orb", 7: "Chromatic Orb", 8: "Jeweller's Orb", 9: "Orb of Chance",
                 10: "Cartographer's Chisel", 11: "Orb of Scouring", 13: "Orb of Regret", 14: "Regal Orb",
                 15: "Divine Orb", 16: "Vaal Orb", 17: "Scroll of Wisdom", 18: "Portal Scroll", 19: "Armourer's Scrap,",
                 20: "Blacksmith's Whetstone", 21: "Glassblower's Bauble", 22: "Orb of Transmutation",
                 23: "Orb of Augmentation", 24: "Mirror of Kalandra", 25: "Eternal Orb", 26: "Perandus Coin",
                 27: "Silver Coin"}

# same as above, but order different: key = name, value = ID
currencies = {"Orb of Alteration": 1, "Orb of Fusing": 2, "Orb of Alchemy": 3, "Chaos Orb": 4, "Gemcutter's Prism": 5,
              "Exalted Orb": 6, "Chromatic Orb": 7, "Jeweller's Orb": 8, "Orb of Chance": 9, "Cartographer's Chisel": 10,
              "Orb of Scouring": 11, "Orb of Regret": 13, "Regal Orb": 14, "Divine Orb": 15, "Vaal Orb": 16,
              "Scroll of Widsom": 17, "Portal Scroll": 18, "Armourer's Scrap": 19, "Blacksmith's Whetstone": 20,
              "Glassblower's Bauble": 21, "Orb of Transmutation": 22, "Orb of Augmentation": 23,
              "Mirror of Kalandra": 24, "Eternal Orb": 25, "Perandus Coin": 26, "Silver Coin": 27}


def get_price(want_currency, have_currency="Chaos Orb"):
    """ General method for searching for the price of a given Currency item in Path of Exile.

        This method is easily reusable and makes it easier to search for specific currency items.

        Once it has its items and the sum of them, it performs a median calculation, to find the "more correct" pricing
        than just the first item could bring (might be a bot/troll pricing it way lower, etc.).

        Instead of using the dict(s), you could also only take the ID's, though then you would have to memorize them.
        Then you could take the names during the parsing process.
        I think I am happy as it is. Will expand the dict with all the rest of the currency items -
        at least the basic ones soon-ish. ;)

        Uses the bs4 module for faster extracting (instead of selenium).

        :param want_currency: the name of the item to look for (just for better output) - can also be parsed from the page
        :param have_currency: the item name to compare/price against (usually ID 4, i.e. Chaos Orb)

        :return: returns the extracted information
    """

    # if given currency name is NOT in the above dict, return
    if want_currency not in currencies.keys() or have_currency not in currencies.keys():
        return f"This currency item does not exist, please try again."

    # if given currency name is in the above dict, continue here

    # set the item id and the compare item id to the value of their item names
    want_item_id = currencies[want_currency]
    have_item_id = currencies[have_currency]

    # if both lookup item and compare item are Chaos, set the compare item to Exalts
    if want_item_id == 4 and have_item_id == 4:
        have_item_id = 6
        have_currency = "Exalted Orb"

    currency_url = f"https://currency.poe.trade/search?league=Heist&online=x&stock=&want={want_item_id}&have={have_item_id}"
    site = requests.get(currency_url)
    poetrade = bs4.BeautifulSoup(site.text, "html.parser")

    # a check to see if ANYTHING could be found with the given search criteria
    if "Oopsie! Nothing was found." in poetrade.text:
        return f"Nothing could be found with item '{want_currency}' and comparison item '{have_currency}'."

    # get 5 listings and their pricing, so in order to get a better accurate pricing schema
    display_offers = poetrade.find_all("div", class_="displayoffer", limit=5)  # up to 5, might not find them all

    # instead of such a solution, you could also just walk down the page elements even more, and get the needed
    # elements like that, but for now it is working like a charm

    nth_child = 3  # the element to look for, for some searches it starts at 4, and others 3 - see check down here
    items = []
    for offer in display_offers:  # since limit=5 above, it only contains UP TO that many page elements
        item = offer.select_one(f"div.displayoffer:nth-child({nth_child}) > div:nth-child(1) "
                                "> div:nth-child(1) > small:nth-child(1)")
        if item is None:  # for whatever reason, some searches for other currencies result in item = None,
            # 'cause of the nth_child here. For many it starts at 4, and for others it starts at 3, hence the check here
            item = offer.select_one(f"div.displayoffer:nth-child({nth_child + 1}) > div:nth-child(1) "
                                    "> div:nth-child(1) > small:nth-child(1)")

        items.append(item.text)
        nth_child += 1

    matches = []

    # https://stackoverflow.com/questions/4289331/how-to-extract-numbers-from-a-string-in-python/61134895#61134895
    # ^ Credit to this person for the following small section
    # pattern = "[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+"
    pattern = r"[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+"  # "|" to separate multiple patterns
    joined_items = "   ".join(items)
    if re.search(pattern, joined_items) is not None:
        for catch in re.finditer(pattern, joined_items):
            # print(catch[0])  # catch is a match object
            matches.append(catch[0])
            # it still catches the single "1"'s there, but not sure how to completely avoid that :/
            # will just write each catch[0] into a list, and then simply take every 2nd entry in that list LUL
    else:
        return f"Something went wrong... Please try again. If this problem persists, " \
               f"please contact the creator of this Bot."

    matches = matches[1::2]

    # iterate over the entries in the list and add them together
    sum_prices = float(0)
    for num in matches:
        sum_prices += float(num)

    # get the median (rough current price)
    result = sum_prices / len(matches)

    return "One '{}' is worth roughly {:.4f} {}s. 10 roughly {:.4f}. \nURL: {}".format(want_currency,
                                                                                       result,
                                                                                       have_currency,
                                                                                       result * 10,
                                                                                       currency_url)


class PoE(discord.ext.commands.Cog):
    """ PoE (Path of Exile) specific commands """

    @commands.command(name="price",
                      help="Returns back the current rough price of a given currency (in Chaos by default)."
                           "\nOnly the currency name is needed (item you want), optional comparison item name "
                           "(item you have) can be passed too "
                           "(but not needed). Defaults to comparison against: Chaos Orb."
                           "\nNote: names are case sensitive!")
    @commands.guild_only()
    async def get_curr_price(self, ctx, want_currency, have_currency="Chaos Orb"):
        """
        Command:\n
        Looks up the given currency name and its price compared to another currency (usually Chaos Orb).
        Uses the function :get_price(): for the main logic.

        :param ctx: the Context data (gets it from Discord)
        :param want_currency: the currency to search for
        :param have_currency: optional - the name of the currency to make the comparison against
        (defaults to Chaos Orb if left empty)

        :return: sends the extracted information to the channel it was called from
        """

        price_info = get_price(want_currency=want_currency, have_currency=have_currency)
        await ctx.send(f"{price_info}")

    @commands.command(name="exalt",
                      help="Returns back the current rough price of an Exalted Orb."
                           "\nUse the !price command for other currencies.")
    @commands.guild_only()
    async def get_price_exalt(self, ctx):
        """
        Command:\n
        Returns the price of the Exalted Orb only (compared to Chaos Orb).

        For other currencies, use the :get_curr_price(): command function.

        :param ctx: the Context data (gets it from Discord)

        :return: sends the extracted information to the channel it was called from
        """

        want_item = "Exalted Orb"
        have_item = "Chaos Orb"
        price_info = get_price(want_currency=want_item, have_currency=have_item)
        await ctx.send(f"{price_info}")

    @commands.command(name="chaos",
                      help="Returns back the current rough price of an Chaos Orb."
                           "\nUse the !price command for other currencies.")
    @commands.guild_only()
    async def get_price_chaos(self, ctx):
        """
        Command:\n
        Returns the price of the Chaos Orb only (compared to Exalted Orb).

        For other currencies, use the :get_curr_price(): command function.

        :param ctx: the Context data (gets it from Discord)

        :return: sends the extracted information to the channel it was called from
        """

        want_item = "Chaos Orb"
        have_item = "Exalted Orb"
        price_info = get_price(want_currency=want_item, have_currency=have_item)
        await ctx.send(f"{price_info}")

    @commands.command(name="item",
                      help="Searches for a given item and its (at this time) sockets and linked sockets."
                           "A screenshot of the item, "
                           "as well as a direct whisper which you can use, will be returned.")
    @commands.guild_only()
    async def get_item(self, ctx, item_of_interest, socket_count_min="6", linked_sockets_min="6"):
        """
        Command:\n
        Searches for a given item on poe.trade and gives back the first found result as a screenshot back.

        As it is now it has very limited use-cases, but will be building upon it to accept more
        additional stats/criteria.

        :param ctx: the Context data (gets it from Discord)
        :param item_of_interest: the name of the item you want to look for
        :param socket_count_min: the min amount of sockets the item should have - defaults to 6 (max amount)
        :param linked_sockets_min: the min amount of linked sockets the item should have - defaults to 6 (max amount)

        :return: a message containing the extracted information to the user/channel it was called from
        """

        # path to the webdriver (geckodriver) for FireFox - either file path or add it to the PATH env. variable
        gecko_path = "..\\Screenshots\\geckodriver-v0.27.0-win32\\geckodriver.exe"

        driver = webdriver.Firefox(executable_path=gecko_path)
        # path to the uBlock .xpi file - needs to be the full file path, otherwise it won't work
        addon_path = "PATH_TO_ADDON_HERE\\uBlock0_1.30.1b3.firefox.signed.xpi"
        driver.install_addon(path=addon_path)
        driver.maximize_window()

        base_url = "https://poe.trade/"
        driver.get(base_url)

        input_item = driver.find_element_by_id("name")
        input_item.send_keys(item_of_interest)  # + Keys.ENTER

        sockets_min = driver.find_element_by_name("sockets_min")
        sockets_min.send_keys(socket_count_min)

        linked_min = driver.find_element_by_name("link_min")
        linked_min.send_keys(linked_sockets_min + Keys.ENTER)  # just press ENTER here, will do more criteria soon

        # a little sleep to the driver/browser ain't to fast for the taking of the screenshots in a moment
        sleep(2)
        # search_button = driver.find_element_by_class_name("search button")
        # search_button.click()

        # a simple check to see if any results came up
        if "Nothing was found. Try widening your search criteria." in driver.page_source:
            return await ctx.send(f"No item with name {item_of_interest} could be found.")

        # if results came up, extract the first item via screenshot(s) and present them to the user

        # the 1st part of the listing - the item screenshot, as well as its stats
        first_item = driver.find_element_by_xpath("/html/body/div[2]/div/div[3]/div/div/div[4]"
                                                  "/div[1]/table/tbody[1]/tr[1]")
        first_item.screenshot("..\\Screenshots\\first_item.png")

        # the 2nd part of the listing - contains the price as well as who is selling it
        sold_by = driver.find_element_by_xpath("/html/body/div[2]/div/div[3]/div/div/div[4]"
                                               "/div[1]/table/tbody[1]/tr[2]")
        sold_by.screenshot("..\\Screenshots\\first_item_sold_by.png")

        # the "Whisper" button on the page - copies the direct whisper into the clipboard
        whisper = driver.find_element_by_xpath("/html/body/div[2]/div/div[3]/div/div/div[4]"
                                               "/div[1]/table/tbody[1]/tr[2]/td[2]/span/ul/li[4]/a")
        whisper.click()

        search_url = driver.current_url
        driver.close()

        """ # credit for the following image merging via PIL to https://stackoverflow.com/a/30228789 
            # using a little modified version, so it doesn't resize the pictures (don't need this in my case)
        """
        # with this here in general, the images need to be of the same dimension(s) (at least other images with
        # with different dimensions (in this case at least different width) are not working) - tried with vstack()
        list_images = ["..\\Screenshots\\first_item.png",
                       "..\\Screenshots\\first_item_sold_by.png"]
        images = [PIL.Image.open(img) for img in list_images]
        # if horizontal alignment, use hstack() - vertical, use vstack()
        images_combined = np.vstack(img for img in images)

        image_final = PIL.Image.fromarray(images_combined)
        image_final.save("..\\Screenshots\\1_item.png")

        await ctx.send(f"@{ctx.author} - see following information regarding your requested search:\n"
                       f"URL: {search_url}"
                       f"\nWhisper: \n{paste()}",  # using pyperclip's .paste() method to paste from the clipboard
                       file=discord.File("..\\Screenshots\\1_item.png"))
        
