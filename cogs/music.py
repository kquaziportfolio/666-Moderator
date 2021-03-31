import re

import discord
import lavalink
from discord.ext import commands

from bot import DarkBot

url_rx = re.compile(r"https?://(?:www\.)?.+")


class Music(commands.Cog):
    """
    Cog for music.\n
    Methods:
        play (ctx, query):
            Joins the users channel, searches for the query, and plays the song.\n
            ctx (commands.Context) - Context\n
            query (str) - Query\n
        disconnect (ctx):
            Disconnects from the channel\n
            ctx (commands.Context) - Context\n
        skip (ctx):
            Skips the current song in the queue.\n
            ctx (commands.Context) - Context\n
        pause (ctx):
            Pauses the queue
            ctx (commands.Context) - Context\n
        unpause (ctx):
            Resumes the queue
            ctx (commands.Context) - Context\n
    """

    def __init__(self, bot):
        self.bot = bot

    async def logout(self):
        print("Bye!")
        self.cog_unload()
        for guildid in self.bot.lavalink.player_manager.players:
            player = self.bot.lavalink.player_manager.players[guildid]
            player.queue.clear()
            await player.stop()
            await self.bot.get_guild(guildid).change_voice_state(channel=None)

    @commands.group(invoke_without_command=True)
    async def music(self, ctx: commands.Context):
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Loads in LavaLink, ensuring that all bot methods have been initialized
        """
        bot = self.bot
        if not hasattr(bot, "lavalink"):
            bot.lavalink = lavalink.Client(bot.user.id)
            bot.lavalink.add_node("127.0.0.1", 2463, "testing", "na", "default-node")
            bot.add_listener(bot.lavalink.voice_update_handler, "on_socket_response")

        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        """
        Removes the event hooks
        """
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx: commands.Context):
        """
        Ensures that the bot is in a voice channel with the user.\n
        Args:
             ctx: Context
        """
        guild_check = ctx.guild is not None
        if guild_check:
            await self.ensure_voice(ctx)
        return guild_check

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        """
        On error, print out message in the channel\n
        Args:
             ctx: Context
             error: The error
        """
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)

    async def ensure_voice(self, ctx: commands.Context):
        """
        Confirms that the bot is in a VC with the user\n
        Args:
             ctx: Context
        """
        player = self.bot.lavalink.player_manager.create(
            ctx.guild.id, endpoint=str(ctx.guild.region)
        )
        should_connect = ctx.command.qualified_name in ("music play",)

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandInvokeError("Join a voicechannel first.")

        if not player.is_connected:
            if not should_connect:
                raise commands.CommandInvokeError("Not connected.")

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                raise commands.CommandInvokeError(
                    "I need the `CONNECT` and `SPEAK` permissions."
                )

            player.store("channel", ctx.channel.id)
            await ctx.guild.change_voice_state(channel=ctx.author.voice.channel)
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError("You need to be in my voicechannel.")

    async def track_hook(self, event: lavalink.Event):
        """
        Disconnects from the channel if the Queue is done\n
        Args:
            event: The event
        """
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            guild = self.bot.get_guild(guild_id)
            await guild.change_voice_state(channel=None)

    @music.command(aliases=["p"])
    async def play(self, ctx, *, query: str):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        query = query.strip("<>")
        if not url_rx.match(query):
            query = f"ytsearch:{query}"
        results = await player.node.get_tracks(query)
        if not results or not results["tracks"]:
            return await ctx.send("Nothing found!")

        embed = discord.Embed(color=discord.Color.blurple())

        # Valid loadTypes are:
        #   TRACK_LOADED    - single video/direct URL)
        #   PLAYLIST_LOADED - direct URL to playlist)
        #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
        #   NO_MATCHES      - query yielded no results
        #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]

            for track in tracks:
                # Add all of the tracks from the playlist to the queue.
                player.add(requester=ctx.author.id, track=track)

            embed.title = "Playlist Enqueued!"
            embed.description = (
                f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
            )
        else:
            tracks = results["tracks"][:10]
            i = 0
            q = ""
            for track in tracks:
                i += 1
                q += f"{i}) {track['info']['title']} - {track['info']['uri']}\n"
            embed = discord.Embed()
            embed.description = q
            embed.title = "Music Selector 9000"
            await ctx.channel.send(embed=embed)
            response = await self.bot.wait_for(
                "message",
                check=lambda m: (
                    (m.author.id == ctx.author.id) and (m.content.isnumeric())
                ),
            )
            track = tracks[int(response.content) - 1]
            embed.title = "Track Enqueued"
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)

        await ctx.send(embed=embed)
        if not player.is_playing:
            await player.play()

    @music.command(aliases=["dc"])
    async def disconnect(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send("Not connected.")

        if not ctx.author.voice or (
            player.is_connected
            and ctx.author.voice.channel.id != int(player.channel_id)
        ):
            return await ctx.send("You're not in my voicechannel!")
        player.queue.clear()
        await player.stop()
        await ctx.guild.change_voice_state(channel=None)
        await ctx.send("(⌐■_■)  | Disconnected.")

    @music.command()
    async def skip(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.send("Not connected.")
        await player.skip()

    @music.command()
    async def pause(self, ctx):
        await self.bot.lavalink.player_manager.get(ctx.guild.id).set_pause(True)

    @music.command(aliases=["resume"])
    async def unpause(self, ctx):
        await self.bot.lavalink.player_manager.get(ctx.guild.id).set_pause(False)


def setup(bot: DarkBot):
    """
    Setup the bot
    """
    bot.add_cog(Music(bot))
