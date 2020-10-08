""" PoE (Path of Exile) SPECIFIC COMMANDS

Copyright © 2020 https://github.com/sixP-NaraKa - and all that shit.
Testing the Discord Bot functions and stuff.
"""


import re
from time import sleep

import discord
from discord.ext import commands
from selenium.webdriver.common.keys import Keys
from pyperclip import paste

from API.DiscordBot.standard_functions_bot import get_parser, initialize_driver


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

    currency_url = f"https://currency.poe.trade/search?league=Heist&online=x&stock=&" \
                   f"want={want_item_id}&have={have_item_id}"
    poetrade = get_parser(currency_url)

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

    # get the compare item name via its ID - not really needed anymore, since we have it above already, but whatever
    # comp_item_name = currency_dict[have_item_id]
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
                      help="Searches for a given item and its (at this time) sockets, linked sockets and colouring. "
                           "Returns the first 6 results, "
                           "as well as with direct whispers which you can use.",
                      ignore_extra=False)
    @commands.guild_only()
    async def get_item(self, ctx, item_of_interest, colour_s_l, *args: int):  # :int triggers error if can't convert
        """
        Command:\n
        Searches for a given item on poe.trade and gives back the first 6 found results as screenshots back.
        Including the whisper to be able to message the seller directly straight away.

        Sends the results per DM to the user who called this command.

        As it is now it has very limited use-cases, but will be building upon it to accept more
        additional stats/criteria.
        Added some more criteria (concerning colouring of the sockets), but of course limited use-cases still apply,
        because many items have specific stats one wants to look out for, and not only the sockets, etc..
        This command never was intended to be super complex or anything, was just wanting to do something like this. ;)

        :param ctx: the Context data (gets it from Discord)
        :param item_of_interest: the name of the item you want to look for
        :param colour_s_l: user decides to search for socket colours or linked colours - "l" for linked, "s" for socket
        :param args: additional criteria - is being used to get socket counts (sockets & links), as well as
                     the colouring of the individual sockets (r g b w)
                     and set them according to the order of input

        :return: a message containing the extracted information to the user/channel it was called from
        """

        # check to see if colour_s_l is either l or s, otherwise notify user
        if colour_s_l.lower() != "l" and colour_s_l.lower() != "s":
            return await ctx.send(f"Passed through colour parameter '{colour_s_l}' does not match 's' (sockets only) "
                                  f"or 'l' (links only).")

        # possible check to also make: see if any of the numbers is smaller than 0, if so, return back and notify user
        if len(args) >= 6:
            socket_count_min, linked_sockets_min, r, g, b, w = args[0:6:1]

            # check to see if the number of the sockets is lower than that of the linked socket
            if socket_count_min < linked_sockets_min:
                return await ctx.send(f"The number of Sockets '{socket_count_min}' is lower "
                                      f"than the number of Links '{linked_sockets_min}'.")

            # also there as a check to see if the inputted numbers can be converted to int
            # NO NEED FOR THIS HONESTLY, SINCE THE CONVERSION AT FUNCTION TOP PARAM *args ALREADY THROWS ERROR
            # IF CANNOT CONVERT TO INT
            try:
                socket_colour_sum = sum([int(r), int(g), int(b), int(w)])
            except TypeError as te:
                return await ctx.send(f"One or more of the given Socket Colours "
                                      f"cannot be converted to the needed datatype (int):"
                                      f"\n{te.__str__()}")
            if socket_colour_sum > socket_count_min:  # and/or > than linked_sockets_min
                return await ctx.send(f"The sum of the Socket Colours '{socket_colour_sum}' cannot exceed "
                                      f"the number of Sockets '{socket_count_min}' to look for.")
        else:
            return await ctx.send(f"Error: expected 6 additional criteria, got {len(args)}")

        driver = initialize_driver(driver="Firefox", addon_ublock=True)
        # weird ass checks, will add more to them
        if type(driver) == str:
            if "PATH" in driver:
                return await ctx.send("The webdriver could not be initialized. The webdriver path may be missing or "
                                      "something unexpected happened. \nPlease contact the creator of this Bot.")
            return await ctx.send("Could not find the webdriver specified.\nIf the problem persists, "
                                  "contact the creator of this Bot.")

        base_url = "https://poe.trade/"
        driver.get(base_url)

        input_item = driver.find_element_by_id("name")
        input_item.send_keys(item_of_interest)

        sockets_min = driver.find_element_by_name("sockets_min")
        if int(socket_count_min) != 0: sockets_min.send_keys(socket_count_min)

        linked_min = driver.find_element_by_name("link_min")
        if int(linked_sockets_min) != 0: linked_min.send_keys(linked_sockets_min)

        # checking what the user passed through as the <colour> param
        # if it starts with "l" the r g b w variables will be used to colour the linked sockets
        # anything else are the sockets in general
        if colour_s_l.lower().startswith("l"):
            red = driver.find_element_by_name("sockets_r")
            green = driver.find_element_by_name("sockets_g")
            blue = driver.find_element_by_name("sockets_b")
            white = driver.find_element_by_name("sockets_w")
        else:
            red = driver.find_element_by_name("linked_r")
            green = driver.find_element_by_name("linked_g")
            blue = driver.find_element_by_name("linked_b")
            white = driver.find_element_by_name("linked_w")

        if int(r) != 0: red.send_keys(r)
        if int(g) != 0: green.send_keys(g)
        if int(b) != 0: blue.send_keys(b)
        if int(w) != 0: white.send_keys(w)

        # just get something else to click and press enter if above checks
        # (to add the criteria to the search form) here failed
        level_min = driver.find_element_by_name("rlevel_min")
        level_min.send_keys(Keys.ENTER)

        # a little sleep to the driver/browser ain't so fast
        sleep(1)

        # a simple check to see if any results came up
        if "Nothing was found. Try widening your search criteria." in driver.page_source:
            driver.close()
            return await ctx.send(f"No item with name '{item_of_interest}' could be found.")

        # if results came up, extract the first item via screenshot(s) and present them to the user

        # iterate over the first table containing UP TO the first 6 results
        # if you want more results returned, simply increase the UPT TO number!
        saved_screenshots = []
        whispers = []
        for i in range(0, 6, 1):
            try:
                file_path = "..\\Screenshots\\table_1_item_" + str(i) + ".png"
                item = driver.find_element_by_id("item-container-" + str(i))
                item.screenshot(filename=file_path)
                saved_screenshots.append(file_path)
                # depending on if "scam" warning appears, whisper xpath changes
                # + 1 for the whisper since they start at 1
                if "Don't fall for this scam, click here for more info." in driver.page_source:
                    whisper = driver.find_element_by_xpath(f"/html/body/div[2]/div/div[3]/div/div/div[5]/div/"
                                                           f"table/tbody[" + str(i + 1) + "]/tr[2]/td[2]/span/ul/li[4]/a")
                else:
                    whisper = driver.find_element_by_xpath("/html/body/div[2]/div/div[3]/div/div/div[4]/div[1]/"
                                                           "table/tbody[" + str(i + 1) + "]/tr[2]/td[2]/span/ul/li[4]/a")
                    
                whisper.click()
                whispers.append(paste())
            # sleep(1)
            except Exception as e:
                print(f"At run {i}:", e)

        current_url = driver.current_url
        driver.close()

        # might do a separate function for sending dms with images
        user = ctx.author
        guild = ctx.guild
        channel = ctx.channel
        category = channel.category
        command = ctx.command
        await ctx.send("Check your DM for the results!")
        await user.create_dm()
        await user.dm_channel.send(f"This DM has been triggered by command '!{command}' "
                                   f"from guild/server '{guild}' in channel '{channel}' (in category '{category}')."
                                   f"\n\nHere are your requested results for '{item_of_interest}' with criteria -  "
                                   f"Sockets: {socket_count_min}, Linked: {linked_sockets_min}, "
                                   f"Socket Colours: {r}r {g}g {b}b {w}w for {colour_s_l} (s = sockets, l = links)"
                                   f"- :bell: :bell: :bell:"
                                   f"\nURL: {current_url}")
        for count, screenshot in enumerate(saved_screenshots):
            await user.dm_channel.send(f"\n{whispers[count]}",
                                       file=discord.File(screenshot))
