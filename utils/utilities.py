""" HERE START THE GENERAL FUNCTIONS """


import requests
import sys

import discord
# import asyncio.base_events as ass
import bs4
from selenium import webdriver
import numpy as np
import PIL
from PIL import Image


# gecko_path = "..\\resources\\geckodriver\\geckodriver-v0.27.0-win32\\geckodriver.exe"
gecko_path = "..\\DiscordBot\\resources\\geckodriver-v0.27.0-win32\\geckodriver.exe"
ublock_addon_ff = "C:\\Users\\IEUser\\IdeaProjects\\DiscordBot\\resources\\ublockXPI\\uBlock0_1.30.1b3.firefox.signed.xpi"


async def stop_bot(ctx):
    """
    Just kill the whole process. Easier that way. LOL
    :param ctx: the Context data (gets it from the calling function)
    """

    bot = ctx.bot
    # bot.ass.BaseEventLoop.stop()
    await bot.logout()
    await bot.close()
    sys.exit(0)


async def send_dm(user, guild, category, channel, command, text, info=""):
    """
    A function to send a user whatever text this function has received.

    :param user: the message receiving user
    :param guild: the guild in which the Bot command call has been made from
    :param category: the category the command came from (if applicable) - None if the channel is not under a category
    :param channel: the channel in which the command has been called in
    :param command: the command which triggered sending this DM (direct message)
    :param text: what text to send the user via a DM (direct message)
    :param info: optional additional information, which the user might find useful

    :return: nothing needs to be returned
    """

    # category = channel.category
    await user.create_dm()
    await user.dm_channel.send(f"This DM has been triggered by command '!{command}' "
                               f"from guild/server '{guild}' in channel '{channel}' (in category '{category}').\n"
                               f"\n{info}"
                               f"\n{text}")


async def send_file_dm(user, guild, category, channel, command, text, info="", file: discord.File = ""):
    """

    :param user: the message receiving user
    :param guild: the guild in which the Bot command call has been made from
    :param category: the category the command came from (if applicable) - None if the channel is not under a category
    :param channel: the channel in which the command has been called in
    :param command: the command which triggered sending this DM (direct message)
    :param text: what text to send the user via a DM (direct message)
    :param info: optional additional information, which the user might find useful
    :param file: an optional parameter to pass the function a file

    :return: nothing needs to be returned
    """

    await user.create_dm()
    await user.dm_channel.send(f"This DM has been triggered by command '!{command}' "
                               f"from guild/server '{guild}' in channel '{channel}' (in category '{category}').\n"
                               f"\n{info}"
                               f"\n{text}",
                               file=file)


def get_request_response(link, json=True):
    """
    Returns only the request response - in json format if desired (for API calls, etc.).

    :param link: the link to get a request from
    :param json: return in json format if desired - defaults to True if left empty

    :return: the plain response - in json format if json=True
    """

    response = requests.get(link)
    if json:
        return response.json()
    else:
        return response


def get_parser(link):
    """
    Returns a bs4 (BeautifulSoup) parser from the given URL.

    :param link: the link to get a request from

    :return: the BeautifulSoup object
    """

    response = requests.get(link)
    parser = bs4.BeautifulSoup(response.text, "html.parser")
    return parser


def initialize_driver(driver, addon_ublock=True):
    """
    Initializes a given driver (selenium).

    :param driver: the name of the driver to initialize
    :param addon_ublock: addon to install with the initialization of the driver - defaults to True

    :return: the initialized driver
    """

    if driver == "Firefox":
        # try:
        #     driver = webdriver.Firefox(executable_path=gecko_path)
        #     if addon_ublock:
        #         driver.install_addon(ublock_addon_ff)
        #     driver.maximize_window()
        # except Exception as ex:
        #     return str(ex)
        driver = webdriver.Firefox(executable_path=gecko_path)
        driver.install_addon(ublock_addon_ff)
        return driver
    else:
        return f"No driver with name {driver} could be found."


def merge_images(list_images, file_name):
    """
    Merges n images together (careful about the dimensions!).
    Might not look good depending on the dimensions of the images used. :D

    :param list_images: list of images to be merged together
    :param file_name: the file_name to save the merged image file under - overwrites existing ones!

    :return: the filepath to the merged image file
    """

    """ # credit for the following image merging via PIL to https://stackoverflow.com/a/30228789
        # using a little modified version, so it doesn't resize the pictures (don't need this in my case)
        # additionally, merging might not even be necessary here, since you can also just take the whole item table
    """
    # with this here in general, the images need to be of the same dimension(s) (at least other images with
    # with different dimensions (in this case at least different width) are not working) - tried with vstack()
    images = [PIL.Image.open(img) for img in list_images]
    # if horizontal alignment, use hstack() - vertical, use vstack()
    images_combined = np.vstack(img for img in images)

    image_final = PIL.Image.fromarray(images_combined)
    image_final_path = f"..\\resources\\screenshots\\{file_name}.png"
    image_final.save(image_final_path)

    return image_final_path
