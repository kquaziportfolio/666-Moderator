import discord
from discord.ext import commands
import asyncio
import json
import time
from jishaku.help_command import *



class Help(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.og=self.bot.help_command
        self.bot.help_command=commands.MinimalHelpCommand()
        self.bot.help_command.cog=self

class Admin(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
    @commands.command()
    @commands.is_owner()
    async def blacklist(self,ctx,member:discord.Member):
        with open("blist.txt","a") as f:
            f.write(str(member.id))
            f.write("\n")
    


def setup(bot):
    bot.add_cog(Help(bot))
    bot.add_cog(Admin(bot))
    print("Loaded Admin")
