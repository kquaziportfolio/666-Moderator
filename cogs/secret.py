import discord
from discord.ext import commands
import asyncio
import json
import time

class Secret(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command(aliases=["$$$$"],hidden=True)
    @commands.is_owner()
    async def say(self,ctx,*,message):
        await ctx.message.delete()
        print(message)
        await ctx.send(message)
        self.bot.unload_extension(f"cogs.secret")
        

def setup(bot):
    bot.add_cog(Secret(bot))
