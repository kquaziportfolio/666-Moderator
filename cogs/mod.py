import asyncio
import subprocess as sp
import time
import typing

import discord
from discord.ext import commands

from bot import DarkBot

permerrortext = "You do not have sufficient permissions to execute this command"
permerrortext += ", if you believe this is in error, please contact either thepronoobkq#3751 (owner of the bot) by "
permerrortext += "DM, or contact a server admin or owner (to get you perms)"


def proctime(d):
    """
    Convers D to an integer in seconds
    Args:
        d (str): Duration
    Returns:
        int: Time in seconds of duration
    """
    t = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    suffix = d[-1]
    d = int(d[:-1])
    d = d * t[suffix]
    return d


def canban(ctx, member: discord.Member):
    """
    Can member ban in CTX
    Returns:
        bool: Can ban?
    """
    return member.permissions_in(ctx.channel).ban_members


def cankick(ctx, member: discord.Member):
    """
    Can member kick in CTX
    Returns:
        bool: Can kick?
    """
    return member.permissions_in(ctx.channel).kick_members


def candelete(ctx, member: discord.Member):
    """
    Can member delete messages in CTX
    Returns:
        bool: Can delete?
    """
    return member.permissions_in(ctx.channel).manage_messages


def formatter(inf: dict):
    """
    Returns:
        str: Formatted string
    """
    s = f"__**Case {inf['case']}**__: **VICTIM** - {inf['victim']}, **ACTION** - {inf['action']}, **Moderator** - {inf['author']}, **Duration** - {inf['duration']}"
    s += f" **REASON** - {inf['reason']}"
    return s


class Moderation(commands.Cog):
    """
    Main moderation cog. This handles all mod commands including kicks, bans, mutes, warns, and cases.

    Methods:
        ban(ctx, victim, reason = None):
            Bans victim from the server with the audit-log reason as REASON or a default message if reason==None\n
            ctx (commands.Context) - Context of the command  (issuer, server, channel, etc)\n
            victim (discord.User) - Victim to ban\n
            reason (str) - Reason of ban\n
        case(ctx, num):
            Retrives a case from its number\n
            ctx (commands.Context) - Context of the command  (issuer, server, channel, etc)\n
            num (int) - The integer ID to retrieve\n
        clear(ctx, num, member=None):
            Clear a number of messages, optionally from member\n
            ctx (commands.Context) - Context of the command  (issuer, server, channel, etc)\n
            num (int) - The number of messages to clear\n
            member (discord.User) - Optionally only clear messages by this member\n
        clearlogs(ctx, member, reason=None):
            Clears the logs of member\n
            ctx (commands.Context) - Context of the command  (issuer, server, channel, etc)\n
            member (discord.User) - The member to clear logs of\n
            reason (str) - Reason\n
        clearserver(ctx):
            Clears all infractions in the server\n
            ctx (commands.Context) - Context of the command  (issuer, server, channel, etc)\n
        infractions(ctx,victim):
            Retrieves all infractions by victim and pretty-print the output\n
            ctx (commands.Context) - Context of the command (issuer, server, channel, etc)\n
            victim (discord.User) - Victim to retrieve infractions from\n
        kick (ctx, victim, reason = None):
            Kicks victim from the server with the audit-log reason as REASON or a default message if reason==None\n
            ctx (commands.Context) - Context of the command  (issuer, server, channel, etc)\n
            victim (discord.User) - Victim to kick\n
            reason (str) - Reason of kick\n
        mute (ctx, victim, d="10", reason=None):
            Mutes member for D time\n
            ctx (commands.Context) - Context of the command  (issuer, server, channel, etc)\n
            victim (discord.User) - Victim\n
            d (str) - A number followed by a letter (if none, assume minute)\n
            reason (str) - Reason\n
        mutes (ctx):
            Gets all active mutes\n
            ctx (commands.Context) - Context of the command  (issuer, server, channel, etc)\n
        mywarns (ctx):
            Gets warns of author\n
            ctx (commands.Context) - Context of the command  (issuer, server, channel, etc)\n
        removecase (ctx, case, reason):
            Removes case\n
            ctx (commands.Context) - Context of the command  (issuer, server, channel, etc)\n
            case (int) - Case to remove\n
            reason (str) - Reason\n
        rr (ctx, a):
            Filler command to allow reaction role bot to run concurrently\n
            ctx (commands.Context) - Context of the command  (issuer, server, channel, etc)\n
            a (str) - Catch all args\n
        serverwarns(ctx):
            Gets all warns in server, sorted by most warns to least\n
            ctx (commands.Context) - Context of the command  (issuer, server, channel, etc)\n
        softban(ctx, victim, reason=None):
            Softbans victim to remove all messages\n
            ctx (commands.Context) - Context of the command  (issuer, server, channel, etc)\n
            victim (discord.User) - Victim\n
            reason (str) - Reason\n
        tempban(ctx, victim, duration, reason=None):
            DEPRECATED - Temporarily bans victim for duration\n
            ctx (commands.Context) - Context of the command  (issuer, server, channel, etc)\n
            duration (str) - Duration
            Reason (str) - Reason
        unban(ctx, victim, reason=None):
            Unbans victim\n
            ctx (commands.Context) - Context of the command  (issuer, server, channel, etc)\n
            victim (discord.User) - Victim\n
            reason (str) - Reason\n
        unmute(ctx, victim, reason=None):
            Unmutes victim\n
            ctx (commands.Context) - Context of the command  (issuer, server, channel, etc)\n
            victim (discord.User) - Victim\n
            reason (str) - Reason\n
        warn(ctx, victim, reason):
            Warns victim
            ctx (commands.Context) - Context of the command  (issuer, server, channel, etc)\n
            victim (discord.User) - Victim\n
            reason (str) - Reason\n
    """

    def __init__(self, bot: DarkBot):
        self.bot = bot

    @commands.command(aliases=["warns"])
    async def infractions(self, ctx: commands.Context, victim: discord.User):
        if not (candelete(ctx, ctx.author)):
            return
        s = ""
        for inf in self.bot.logger.col.find({"victim": victim.id}):
            inf["author"] = ctx.guild.get_member(inf["author"])
            inf["victim"] = ctx.guild.get_member(inf["victim"])
            s += formatter(inf)
            s += "\n"
        if s == "":
            s = "This member is a good person! Or baby jesus"
        await ctx.send(s)

    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason="None"):
        author = ctx.author
        if cankick(ctx, author):
            await member.kick(reason=f"Manual kick by {author}:\n{reason}")
            await ctx.send(f"Kicked {member} for reason:\n{reason}")
            self.bot.logger.write(author, "KICK", member, reason)

    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason="None"):
        author = ctx.author
        if canban(ctx, author):
            await member.ban(reason=f"Manual ban by {author}:\n{reason}")
            await ctx.send(f"Banned {member} for reason:\n{reason}")
            self.bot.logger.write(author, "BAN", member, reason)

    @commands.command()
    async def unban(self, ctx, member: discord.User, *, reason="None"):
        author = ctx.author
        if canban(ctx, author):
            await ctx.guild.unban(member, reason=f"Manual unban by {author}:\n{reason}")
            await ctx.send(f"Unbanned {member} by {author} for reason:\n{reason}")
            self.bot.logger.write(author, "UNBAN", member, reason)

    @commands.command()
    async def softban(self, ctx, member: discord.Member, *, reason="None"):
        author = ctx.author
        if canban(ctx, author):
            await member.ban(reason=f"Manual softban by {author} for reason:\n{reason}")
            await member.unban(
                reason=f"Manual softban by {author} for reason:\n{reason}"
            )
            await ctx.send(f"Softbanned {member} for reason:\n{reason}")
            self.bot.logger.write(author, "SOFTBAN", member, reason)

    @commands.command()
    async def tempban(self, ctx, member: discord.Member, duration, *, reason="None"):
        await ctx.send("dont use me!!!!!!!!!11!!!11111!")
        return
        author = ctx.author
        d = duration
        if d.isnumeric():
            d += "m"
        try:
            t = time.time() + proctime(d)
        except Exception as e:
            await ctx.send("Error: " + repr(e))
        duration = d
        if canban(ctx, author):
            await member.ban(
                reason=f"Manual tempban by {author} for duration:{duration} and reason:\n{reason}"
            )
            self.bot.logger.tempdata["bans"][member.id] = t
            self.bot.logger.write(author, "TEMPBAN", member, reason, d)

    @commands.command()
    async def mute(self, ctx, member: discord.Member, d="10", *, reason="None"):
        author = ctx.author
        if d.isnumeric():
            d += "m"
        try:
            t = time.time() + proctime(d)
        except Exception as e:
            await ctx.send("Error: " + repr(e))
        duration = d
        if candelete(ctx, author):
            self.bot.logger.tempdata["mutes"][member.id] = (member, t)
            print(self.bot.logger.tempdata)
            await ctx.send(
                f"Muted {member} for duration: {duration}\nreason:\n{reason}"
            )
            self.bot.logger.write(author, "MUTE", member, reason, d)

    @commands.command()
    async def unmute(self, ctx, member: discord.Member, *, reason="None"):
        author = ctx.author
        if candelete(ctx, author):
            try:
                del self.bot.logger.tempdata["mutes"][member.id]
            except:
                await ctx.send("They arent muted. duh")
                return
            await ctx.send(f"Unmuted {member}\nreason:\n{reason}")
            self.bot.logger.write(author, "UNMUTE", member, reason)

    @commands.command()
    async def mutes(self, ctx):
        await ctx.send("Current mutes:")
        d = self.bot.logger.tempdata["mutes"]
        a = {}
        for k in d:
            v = d[k]
            a[ctx.guild.get_member(v)] = v
        await ctx.send(a)

    @commands.command()
    async def case(self, ctx, num):
        if not (candelete(ctx, ctx.author)):
            return
        case = self.bot.logger.read_case(int(num))
        case["victim"] = ctx.guild.get_member(case["victim"])
        case["author"] = ctx.guild.get_member(case["author"])
        if case == None:
            case = "This case does not exist"

        else:
            case = formatter(case)
        await ctx.send(case)

    @commands.command()
    async def warn(self, ctx, member: discord.Member, *, reason):
        if candelete(ctx, ctx.author):
            await ctx.send("Warned")
            self.bot.logger.write(ctx.author, "WARN", member, reason)

    @commands.command()
    async def clearlogs(self, ctx, member: discord.User, *, reason):
        if candelete(ctx, ctx.author):
            if ctx.author.id in [710669508779573311, 544699702558588930]:
                await ctx.send("Removed warnings, this actions **is** logged")
                self.bot.logger.col.delete_many({"victim": member.id})
                self.bot.logger.write(ctx.author, "REMOVE ALL CASES", member, reason)
            else:
                await ctx.send("no")

    @commands.command()
    async def rr(self, ctx, *, a):
        pass

    @commands.command()
    async def mywarns(self, ctx):
        victim = ctx.author
        s = ""
        for inf in self.bot.logger.col.find({"victim": victim.id}):
            inf["author"] = ctx.guild.get_member(inf["author"])
            inf["victim"] = ctx.guild.get_member(inf["victim"])
            s += formatter(inf)
            s += "\n"
        if s == "":
            s = "You is a good person! Or baby jesus"
        await ctx.send(s)

    @commands.command()
    async def serverwarns(self, ctx):
        d = self.bot.logger.read_warns()
        a = {}
        for k in d:
            item = k
            print("a")
            if ctx.guild.get_member(item["victim"]) != None:
                item["victim"] = ctx.guild.get_member(item["victim"])
            try:
                a[item["victim"]].append(item)
            except:
                a[item["victim"]] = [item]
        d = {}
        for k in a:
            d[str(k)] = len(a[k])
        s = ""
        for k in {k: v for k, v in sorted(d.items(), key=lambda item: -item[1])}:
            s += k
            s += ": "
            s += str(d[k])
            s += "\n"
        await ctx.send(s)

    @commands.command()
    async def clearserver(self, ctx):
        if ctx.author.id in [710669508779573311, 544699702558588930]:
            self.bot.logger.col.delete_many({})
            sp.run(["clearwarns"], shell=True)
            await ctx.send("This action is not reversible, but it has been completed")

    @commands.command()
    async def removecase(self, ctx, case, *, reason):
        if candelete(ctx, ctx.author):
            back = self.bot.logger.read_case(int(case))
            if (
                ctx.author.id == back["victim"]
                and ctx.author.id != back["author"]
                and not (ctx.author.id in [710669508779573311, 544699702558588930])
            ):
                await ctx.send("You can't remove your own warns. smh")
                return
            await ctx.send("Removed case")
            member = back["victim"]
            self.bot.logger.col.delete_one({"case": int(case)})
            self.bot.logger.write(
                ctx.author,
                "REMOVE CASE",
                ctx.guild.get_member(member),
                reason,
                "INFINITE",
                back,
            )

    @commands.command()
    async def clear(self, ctx, num: int, member: typing.Optional[discord.User] = None):
        count = 0
        l = []
        async for msg in ctx.channel.history():
            if member == None:
                count += 1
                l.append(msg)
            else:
                if msg.author == member:
                    count += 1
                    l.append(msg)
            if count == num:
                break
        await ctx.channel.delete_messages(l)
        t = await ctx.send("Cleared")
        await asyncio.sleep(2)
        await t.delete()


def setup(bot: DarkBot):
    """
    Setup the cog
    """
    bot.add_cog(Moderation(bot))
