# EDIT:
Discord.py (the framework that I use for bot development) is shutting down development, and I personally disagree with Discord on many changes to the APIs and structure of Discord. Due to these reasons, I will no longer develop 666 Moderator, KairanBot (defunct for a while now), or any other Discord bots (except the SCU Discord Bot).



# 666 Moderator
This is the GitHub for a Discord bot that I am working on for the Planet 666 Discord server. This project is built ontop of the <a href="https://discordpy.readthedocs.io/en/latest/">Discord.py</a>
Python project. It uses the Python await/async syntax to route commands to "cogs", which are classes that contain commands and event triggers using the Discord API. The entrypoint is
bot.py, but it requires:
<ul><li>A file named blist.txt that can be empty</li>
<li>A file named num.txt that contains any valid integer (used for log counting)</li>
<li>A file named config.py that has a variable named token with the Discord token</li>
<li>A MongoDB database</li></ul><br>
The code may not be reproducable because it contains specific ID's related to the specific server the project was designed for.

ReadTheDocs is currently broken because it doesn't recognize the stylistic
changes I had to make to register commands in cogs, but the Sphinx documentation
in ./docs/ is working.
