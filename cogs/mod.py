import asyncio
import json
import subprocess as sp
import time
import typing
from pprint import pprint

import discord
from discord.ext import commands
from jishaku.help_command import *

permerrortext = "You do not have sufficient permissions to execute this command"
permerrortext += ", if you believe this is in error, please contact either thepronoobkq#3751 (owner of the bot) by "
permerrortext += "DM, or contact a server admin or owner (to get you perms)"


def proctime(ctx, d):
    t = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    suffix = d[-1]
    d = int(d[:-1])
    d = d * t[suffix]
    return d


def canban(ctx, member: discord.Member):
    return member.permissions_in(ctx.channel).ban_members


def cankick(ctx, member: discord.Member):
    return member.permissions_in(ctx.channel).kick_members


def candelete(ctx, member: discord.Member):
    return member.permissions_in(ctx.channel).manage_messages


def formatter(inf):
    s = f"__**Case {inf['case']}**__: **VICTIM** - {inf['victim']}, **ACTION** - {inf['action']}, **Moderator** - {inf['author']}, **Duration** - {inf['duration']}"
    s += f" **REASON** - {inf['reason']}"
    return s


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["warns"])
    async def infractions(self, ctx, victim: discord.User):
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
            t = time.time() + proctime(ctx, d)
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
            t = time.time() + proctime(ctx, d)
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
            sp.run("clearwarns", shell=1)
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


def setup(bot):
    bot.add_cog(Moderation(bot))
