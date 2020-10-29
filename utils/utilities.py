""" HERE START THE GENERAL FUNCTIONS """


import requests
from pathlib import Path

import discord
import logging
import bs4
from selenium import webdriver
import numpy as np
import PIL
from PIL import Image


logger = logging.getLogger("discord.utilities")

# gecko_path = "..\\resources\\geckodriver\\geckodriver-v0.27.0-win32\\geckodriver.exe"
gecko_path = "..\\DiscordBot\\resources\\geckodriver-v0.27.0-win32\\geckodriver.exe"
ublock_addon_ff = "INSERT_FULL_FILE_PATH_HERE\\DiscordBot\\resources\\ublockXPI\\uBlock0_1.30.1b3.firefox.signed.xpi"


async def embed_message(title: str = None, desc: str = None, color: int = 0x0000FF, filename: str = None) -> discord.Embed:
    """
    Embeds a given message (mostly only useful for bot messages that are made in channels).

    :param title: the title the embed should have
    :param desc: the message (body) the embed should have
    :param color: the color (left side) the embed should have
    :param filename: a optional filename, if you want to embed an image into the embed - is the name as which the file
            will be uploaded as -> filename provided must be the same as the actual image, otherwise no embedded image!

    :returns: the discord.Embed embed
    """

    logger.info("Creating embedded message...")
    embed = discord.Embed(title=title, description=desc, color=color)
    if filename is not None:
        logger.info("Adding attachment to the embed...")
        embed.set_image(url=f"attachment://{filename}")  # i.e. "item.png"
    logger.info("Returning the embed...")
    return embed


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

    logger.info(f"Sending a plain DM to {user}...")
    await user.create_dm()
    await user.dm_channel.send(f"This DM has been triggered by command '!{command}' "
                               f"from guild/server '{guild}' in channel '{channel}' (in category '{category}').\n"
                               f"\n{info}"
                               f"\n{text}")
    logger.info(f"Sent a plain DM to {user}...")


async def send_file_dm(user, guild, category, channel, command, text, info="", file: discord.File = ""):
    """
    A function to send a user whatever text as well as a file this function has received.
    Very similar to the :send_dm: function, but it accepts a file.
    Both can be merged together, actually. But for now will keep them separated.

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

    logger.info(f"Sending a DM with an image to {user}...")
    await user.create_dm()
    await user.dm_channel.send(f"This DM has been triggered by command '!{command}' "
                               f"from guild/server '{guild}' in channel '{channel}' (in category '{category}').\n"
                               f"\n{info}"
                               f"\n{text}",
                               file=file)
    logger.info(f"Sent a DM with an image to {user}...")


def get_request_response(link, json=True):
    """
    Returns only the request response - in json format if desired (for API calls, etc.).

    :param link: the link to get a request from
    :param json: return in json format if desired - defaults to True if left empty

    :return: the plain response - in json format if json=True
    """

    response = requests.get(link)
    if json:
        logger.info("Returning the request response as json...")
        return response.json()
    else:
        logger.info("Returning the request response NOT as json...")
        return response


def get_parser(link):
    """
    Returns a bs4 (BeautifulSoup) parser from the given URL.

    :param link: the link to get a request from

    :return: the BeautifulSoup object
    """

    logger.info("Returning the bs4 parser...")
    response = requests.get(link)
    parser = bs4.BeautifulSoup(response.text, "html.parser")
    return parser


def initialize_driver(driver, addon_ublock=True, headless=True):
    """
    Initializes a given driver (selenium).

    :param driver: the name of the driver to initialize
    :param addon_ublock: addon to install with the initialization of the driver - defaults to True
    :param headless: to set the webdriver to run in headless mode (no UI, etc.) - defaults to True

    :return: the initialized driver
    """

    logger.info(f"Initializing webdriver with following additional criteria: ublock={addon_ublock}, "
                f"headless={headless}")
    if driver == "Firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.headless = headless
        try:
            driver = webdriver.Firefox(executable_path=gecko_path, options=options)
            if addon_ublock:
                driver.install_addon(ublock_addon_ff)
            driver.maximize_window()
        except Exception as ex:
            return str(ex)
        # driver = webdriver.Firefox(executable_path=gecko_path)
        # driver.install_addon(ublock_addon_ff)
        logger.info("Initialized webdriver...")
        return driver
    else:
        logger.info(f"No driver with name {driver} found...")
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

    logger.info(f"Merging images: {list_images} and saving the final image under '{file_name}'...")
    # with this here in general, the images need to be of the same dimension(s) (at least other images with
    # with different dimensions (in this case at least different width) are not working) - tried with vstack()
    images = [PIL.Image.open(img) for img in list_images]
    # if horizontal alignment, use hstack() - vertical, use vstack()
    images_combined = np.vstack(img for img in images)

    image_final = PIL.Image.fromarray(images_combined)
    image_final_path = f"..\\DiscordBot\\resources\\images\\{file_name}.png"
    image_final.save(image_final_path)
    logger.info(f"Merged the images and saved them here: {image_final_path}...")

    return image_final_path


def del_image_files(directory: str = Path.cwd(), patterns: tuple = ("*.png", "*.jpg")):
    """
    Deletes all the found image files in a given directory which match the given pattern (naming).

    :param directory: the directory to look for image files to delete - defaults to the current working directory
    :param patterns: the pattern(s) to which look for image files - defaults to .png and .jpg image files

    :return: will not notify if anything has been deleted / found (errors might still come up though and get printed)
    """

    import os

    path = Path(directory)
    logger.info(f"Prepping to delete files which match pattern(s) '{patterns}' in directory '{directory}'..."
                f"See just below here if anything has been found.")
    for pattern in patterns:
        files = path.glob(pattern)
        found_files = list(files)
        if not found_files:
            # print(f"No file(s) with extension '{pattern}' found. Skipping this extension...")
            logger.info(f"No file(s) with pattern '{pattern}' found. Skipping this pattern...")
            continue
        for file in found_files:
            os.remove(file)
            # print(f"File {file.name} removed...")
            logger.info(f"File {file.name} removed...")
    return


def set_bar_labels(ax, visible_zeros: bool = True):
    """
    For each bar chart in the graph (ax), set the actual value of the bar on top of it (bar label).

    :param ax: the axes to modify the bar labels on
    :param visible_zeros: determines if zero values should be visible on the plot - defaults to True

    :return: the modified axes
    """

    logger.info("Modifying the bar labels to their actual values...")
    # to set the bar label for each bar in the chart with the actual value of the bar
    for rect in ax.patches:
        y_value = rect.get_height()
        x_value = rect.get_x() + rect.get_width() / 2

        space = 3
        va = "bottom"

        if y_value < 0:  # take values <0 also into consideration
            space *= -1
            va = "top"
            
        if visible_zeros is False and y_value == 0:  # don't make it show on the plot (visually)
            continue

        label = "{:.0f}".format(y_value)
        ax.annotate(
            label,
            (x_value, y_value),
            xytext=(0, space),
            textcoords="offset points",
            ha="center",
            va=va,
            rotation=45)

    logger.info("Modified the bar labels in the given chart... Returning the ax(es).")
    return ax
