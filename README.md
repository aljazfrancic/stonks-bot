# Purpose #

The purpose of this Discord bot is to pull the prices of user-defined coins from CoinGecko for a user-defined number of last days and display them in a plot in a relative manner.
The bot will also display prices for the first coin on the list.
Bitcoin halvings inside the CoinGecko interval will also be shown as white vertical lines in case bitcoin is on the list.

# Usage #

To use the bot, send it a direct message on Discord or post in any channel the bot has access to on a Discord server that the bot is in. The message should conform to the following guidelines.

Default settings (maximum number of days available on CoinGecko, using coins bitcoin, ethereum and monero):

    !kekw

will produce something like:
<img src="https://cdn.discordapp.com/attachments/1142735761276420106/1214303302091538552/image.png?ex=65f89f13&is=65e62a13&hm=b1340d5e4cf0ea484544e463736164f62ddd9acc0627db1a5d673012da972a14&">

Default settings with user-defined number of days:

    !kekw <number of days or max>

for example:

    !kekw 200

will produce something like:
<img src="https://cdn.discordapp.com/attachments/1142735761276420106/1214304182048260176/image.png?ex=65f89fe5&is=65e62ae5&hm=7771fdcf6133b305284ed205913d7cd132f2af2ad0483323d6da80015bebeed0&">

Custom input:

    !kekw <number of days or max> <CoinGecko API ids with spaces>

for example:

    !kekw 365 avalanche-2 chainlink monero bitcoin

will produce something like:
<img src="https://cdn.discordapp.com/attachments/1142735761276420106/1214304587717025863/image.png?ex=65f8a046&is=65e62b46&hm=265b20707764539b17996c77b2c9586ef929daa82d67453379f80f4cd9e0c634&">

# Warning #

A bit hacky! Could be improved!
