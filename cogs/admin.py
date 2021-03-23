import discord
from discord.ext import commands


class Admin(commands.Cog):
    """
    Cog for owner-only admin commands.
    Methods:
        blacklist(ctx, member):
            Blacklists a user from using bot commands\n
            ctx (commands.Context) - Context
            member (discord.Member) - User to blacklist
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def blacklist(self, ctx, member: discord.Member):
        with open("blist.txt", "a") as f:
            f.write(str(member.id))
            f.write("\n")


def setup(bot):
    """
    Setup the cog
    """
    bot.add_cog(Admin(bot))
