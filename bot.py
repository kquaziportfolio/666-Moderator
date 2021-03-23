import asyncio
import os
import pathlib
import time
from datetime import datetime as dt

import discord
import lavalink
import pymongo as pym
from discord.ext.commands import *
from jishaku.help_command import *

import config

intents = discord.Intents.all()
print(intents)


class DataLogger:
    def __init__(self, permafile):
        self.permafile = permafile
        self.tempdata = {}
        self.mongo = pym.MongoClient()
        self.db = self.mongo["BotLogger"]
        self.col = self.db["logs"]
        # self.tempdata=self.db["random"].find_one({})
        print(self.tempdata)

    def write(self, author, action, victim, reason, duration="Infinite", backup=None):
        with open("num.txt") as f:
            num = int(f.read())
        with open("num.txt", "w") as f:
            f.write(str(num + 1))
        doc = {
            "author": author.id,
            "action": action,
            "victim": victim.id,
            "reason": reason,
            "stamp": dt.now().strftime("%y/%m/%d:%I:%M:%S"),
            "case": num + 1,
            "duration": duration,
        }
        if not (backup == None):
            doc["backup"] = backup
        self.col.insert_one(doc)

    def read_all(self):
        a = []
        for i in self.col.find():
            a.append(i)
        return a

    def read_warns(self):
        a = self.read_all()
        b = []
        for i in a:
            if i["action"] == "WARN":
                b.append(i)
        return b

    def read_case(self, num):
        return self.col.find_one({"case": num})

    def update(self):
        pass


class RR:
    def __init__(self, permafile):
        self.permafile = permafile
        with open(permafile) as f:
            pass


class DarkBot(Bot):
    def __init__(self, *args, prefix=None, **kwargs):
        super().__init__(prefix, *args, **kwargs)
        self.bad_words = [
            "fuck",
            "shit",
            "ass",
            "whore",
            "bitch",
            "dick",
            "pussy",
            "tit",
            "shrey",
            "tbag",
            "retard",
        ]
        self.bad_words = []
        self.bg_task = self.loop.create_task(self.playingstatus())
        self.mute_task = self.loop.create_task(self.mutecheck())
        self.update_task = self.loop.create_task(self.updatelogger())
        self.logger = DataLogger("logs.txt")
        self.logger.tempdata["mutes"] = {}
        self.games = ["with your life", "VALORANT as Yo Mamma"]
        self.musicbackend = None

    async def on_ready(self):
        status = "Planet 666 | discord.gg/8GMA2M3 | 6!help"
        self.invite = discord.utils.oauth_url(
            self.user.id, discord.Permissions(permissions=8)
        )
        print(
            "Logged in as",
            client.user.name,
            "\nId:",
            client.user.id,
            "\nOath:",
            self.invite,
        )
        print("--------")
        await self.change_presence(
            activity=discord.Game(name=status), status=discord.Status.online
        )

    async def on_message(self, msg: discord.Message):
        ctx = await self.get_context(msg)
        if (
            msg.author.id == 544699702558588930
            and msg.content == "thou shalt be cast in flame"
        ):
            exit()
        for i in self.bad_words:
            if i in "".join(msg.content.split()).lower() and ctx.author.bot == False:
                await msg.delete()
                await ctx.send("stop swearing")
        if ctx.message.author.id in self.logger.tempdata["mutes"]:
            await msg.delete()
        with open("blist.txt") as f:
            a = f.readlines()
        if msg.content.startswith("6!"):
            # await ctx.send("HA!")
            print(a)
            print(ctx.author.id)
            if str(ctx.author.id) + "\n" in a:
                await ctx.send("Blacklisted")
                return
        if msg.content.startswith("6!rr"):
            return
        try:
            await self.process_commands(msg)
        except Exception as e:
            print(e)

    async def logout(self):
        await self.get_cog("Music").logout()
        await super().logout()

    async def on_command_error(self, ctx, error):
        await ctx.send(error)

    async def process_commands(self, message):
        await super().process_commands(message)

    async def playingstatus(self):
        await self.wait_until_ready()
        while self.is_ready():
            status = "Planet 666 | discord.gg/8GMA2M3 | 6!help"
            await self.change_presence(
                activity=discord.Game(name=status), status=discord.Status.online
            )
            await asyncio.sleep(120)

    async def mutecheck(self):
        await self.wait_until_ready()
        while self.is_ready():
            for key in self.logger.tempdata["mutes"]:
                value = self.logger.tempdata["mutes"][key]
                print(key, value)
                if value[0] <= time.time():
                    del self.logger.tempdata["mutes"][key]
            await asyncio.sleep(10)

    async def updatelogger(self):
        await self.wait_until_ready()
        while self.is_ready():
            self.logger.update()
            await asyncio.sleep(10)

    @property
    def connection(self):
        return self._connection


if __name__ == "__main__":
    client = DarkBot(
        intents=intents,
        prefix=when_mentioned_or("6!"),
        help_command=commands.MinimalHelpCommand(),
    )
    nocogs = ["secret"]
    for file in os.listdir("cogs"):
        if file.endswith(".py") and not (file[:-3] in nocogs):
            name = file[:-3]
            try:
                client.load_extension(f"cogs.{name}")
                print(f"Loaded cog {name}")
            except Exception as e:
                print(f"Failed to load cog {name} due to error\n", e)
    client.load_extension("jishaku")
    try:
        client.run(config.token)
    except:
        print("Bye!")
        raise
        # exit()
