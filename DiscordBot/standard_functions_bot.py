""" HERE START THE GENERAL FUNCTIONS

Copyright © 2020 https://github.com/sixP-NaraKa - and all that shit.
Testing the Discord Bot functions and stuff.
"""


async def send_dm(user, guild, category, channel, command, text, info=""):
    """
    A method to send a user whatever text this method has received.

    :param user: the message receiving user
    :param guild: the guild in which the Bot command call has been made from
    :param channel: the channel in which the command has been called in
    :param command: the command which triggered sending this DM (direct message)
    :param text: what text to send the user via a DM (direct message)
    :param info: optional additional information, which the user might find useful

    :return: nothing needs to be returned
    """

    await user.create_dm()
    await user.dm_channel.send(f"This DM has been triggered by command '!{command}' "
                               f"from guild/server '{guild}' in channel '{channel}' (in category '{category}').\n"
                               f"\n{info}"
                               f"\n{text}")
