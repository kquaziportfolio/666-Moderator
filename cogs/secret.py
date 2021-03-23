import asyncio
import json
import time

import discord
from discord.ext import commands


class Secret(commands.Cog):
    """
    Secret commands not loaded by default
    Methods:
        say (ctx, message):
            Repeats message (great for trolling (⌐■_■))\n
            ctx (commands.Context) - Context\n
            message (str) - Message to echo
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["$$$$"], hidden=True)
    @commands.is_owner()
    async def say(self, ctx, *, message):
        await ctx.message.delete()
        print(message)
        await ctx.send(message)
        self.bot.unload_extension(f"cogs.secret")


def setup(bot):
    """
    Setup the cog
    """
    bot.add_cog(Secret(bot))
