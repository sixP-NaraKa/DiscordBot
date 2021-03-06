# DiscordBot - CommandBot

This Discord Bot does, apart from creating channels/categories and deleting them, also a variety of other things, mostly regarding the two games "Age of Empires 2: Definitive Edition (AoE2:DE)" and "Path of Exile (PoE)".

Still testing and finding new things out! Some more or less basic stuff - adding more to it!

That being said, here is a list of the related game commands and what they do!

## AoE2 commands:

- **!online**

*This returns a (still pretty ugly right now) graph showcasing the current amount of players playing AoE2:DE.*

<img src="/resources/images/aoe2_online_stats.png" alt="AoE2:DE stats"/>


- **!top "amount of players" "leaderboard_id"**

*This command is for extracting the current top players from a leaderboard specified by the user.
The default players if number is omitted is 5. The default leaderboard if omitted is 3 (i.e. 1v1 RM).
Available IDs: 1 (1v1 DM), 2 (Team DM), 3 (1v1 RM), 4 (Team RM).
This returns an image containing the number of players of the leaderboard - including their current ranking, their games (wins/losses) and more.
For each 5 players, another graph will be made - all graphs at the end will be merged vertically into one, as can be seen here:*

Example Usage:

*!top 10 3* will yield:

<img src="/resources/images/top_10_players.png" alt="AoE2:DE 1v1 RM leaderboard - Top 10"/>


- **!rank "player name"**

*This command retrieves the current rank, rating, total games played, winrate (%) as well as the current win-streak and the amount of dropped (disconnected) games from a given player. As it is now, only the 1v1 RM leaderboard can be utilized (can be easily enhanced to work with all the leaderboards).
All thanks to the aoe2.net/#api.*

*If the player name is omitted, the current rank #1 player will be returned by default.*

<img src="/resources/images/aoe2_rank_command_discord.png" alt="AoE2:DE - Player stats"/>


## PoE commands:

- **!price "item you want" "item you have"**

*This command is for extracting the current rough price from poe.trade of a currency item you want, compared against a currency item you have.
If the "item you have" is omitted, it will default to "Chaos Orb" if "item you want" is not it as well, otherwise it defaults to "Exalted Orb".
The Bot will reply with the extracted information.*

<img src="/resources/images/price_command_discord.png" alt="Currency Price"/>


- **!chaos** & **!exalt**

*Both commands do the same as the* **!price** *command, but only for the respective item in question (Chaos to Exalt, and Exalt to Chaos) - since both Chaos and Exalted Orbs are the currency items you will most of the time look up the price for.*


- **!item "item name" "socket or links coloured" "6 args to set the amount of sockets and links, and their colours"**

*This command is for extracting information from poe.trade (screenshots of the first 6 results found with the given criteria - as well as a direct whisper to the seller) 
and send them via a DM to the user who invoked this command.
For example:*

<img src="/resources/images/item_command_discord.png" alt="Item information and price"/>
<img src="/resources/images/item_command_dm_discord.png" alt="Item information and price"/>


## Requirements

see: ![requirements.txt](requirements.txt)

## ToDo

a ton! :D Adding more to it as the time goes by!
