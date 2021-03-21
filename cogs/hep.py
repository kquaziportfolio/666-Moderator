import asyncio
import json
import time

import discord
from discord.ext import commands
from jishaku.help_command import *


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.og = self.bot.help_command
        self.bot.help_command = commands.MinimalHelpCommand()
        self.bot.help_command.cog = self


def setup(bot):
    # bot.add_cog(Help(bot))
    pass
