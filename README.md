# DiscordBot - CommandBot
Testing a Discord Bot! Some more or less basic stuff - adding more to it!

This Discord Bot does, apart from creating channels/categories and deleting them, also a variety of other things, mostly regarding the two games "Age of Empires 2: Definitive Edition" and "Path of Exile".

Here is a list of the related game commands and what they do!

## AoE2 commands:

- **!online**

*This returns a (pretty ugly right now) graph showcasing the current amount of players playing AoE2:DE.*

<img src="/resources/images/ao2_stats.png" alt="AoE2:DE stats"/>


- **!top "amount of players"**

*This commmand is for extracting the current 1v1 RM leaderboard specified by the number of players optionally given to this command.
The default players if number is omitted is 5.
This returns a image containing the number of players of the leaderboard.
For each 5 players, another graph will be made - all graphs at the end will be merged vertically into one, as can be seen here:*

<img src="/resources/images/top_10_players.png" alt="AoE2:DE 1v1 RM leaderboard - Top 10"/>


## PoE commands:

- **!price "item you want" "item you have"**

*This command is for extracting the current rough price of a currency item you want, compared against a currency item you have.
If the "item you have" is omitted, it will default to "Chaos Orb" if "item you want" is not it as well, otherwise it defaults to "Exalted Orb".
The Bot will reply with the extracted information.*

<img src="/resources/images/price_command_discord.png" alt="Currency Price"/>


- **!chaos** & **!exalt**

*Both commands do the same as the* **!price** *command, but only for the respective item in question (Chaos to Exalt, and Exalt to Chaos) - since both Chaos and Exalted Orbs are the currency items you will most look up the price for.


- **!item "item name" "socket or links coloured" "6 args to set the amount of sockets and links, and their colours"

*This command is for extracting information (screenshots of the first 6 results of the found results with the gjven criteria 
- as well as a direct whisper to the seller) 
and send them via a DM to the user who invoked this command.
For example:*

<img src="/resources/images/item_command_discord.png" alt="Item information and price"/>
<img src="/resources/images/item_command_dm_discord.png" alt="Item information and price"/>


## Requirements

see: ![requirements.txt](requirements.txt)
