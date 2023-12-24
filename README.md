# Purpose #

The purpose of this Discord bot is to pull the prices for user-defined coins from CoinGecko for a user-defined number of last days and display them in a plot in a relative manner.
The bot will also display prices for the first coin on the list.
Bitcoin halvings inside the CoinGecko interval will also be shown as white vertical lines in case bitcoin is on the list.

# Usage #

Default settings (maximum number of days available on CoinGecko, using coins bitcoin, ethereum and monero):

    !kekw

will produce something like:
<img src="https://media.discordapp.net/attachments/804107481051431013/1188499681760784424/image.png">

Default settings with user-defined number of days:

    !kekw <number of days or max>

for example:

    !kekw 200

will produce something like:
<img src="https://media.discordapp.net/attachments/804107481051431013/1188499937462329344/image.png">

Custom input:

    !kekw <number of days or max> <CoinGecko API ids with spaces>

for example:

    !kekw 365 avalanche-2 chainlink monero bitcoin

will produce something like:
<img src="https://media.discordapp.net/attachments/804107481051431013/1188500389864165386/image.png">

# Warning #

A bit hacky! Could be improved!
