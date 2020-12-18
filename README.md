# 666-Moderator
This is the GitHub for a Discord bot that I am working on for the Planet 666 Discord server. This project is built ontop of the <a href="https://discordpy.readthedocs.io/en/latest/">Discord.py</a>
Python project. It uses the Python await/async syntax to route commands to "cogs", which are classes that contain commands and event triggers using the Discord API. The entrypoint is
bot.py, but it requires:
<ul><li>A file named blist.txt that can be empty</li>
<li>A file named num.txt that contains any valid integer (used for log counting)</li>
<li>A file named config.py that has a variable named token with the Discord token</li>
<li>A MongoDB database</li></ul><br>
The code may not be reproducable because it contains specific ID's related to the specific server the project was designed for.
