import discord
import lavalink
from discord.ext import commands

from bot import DarkBot


class Music(commands.Cog):
    """
    Cog for music related commands
    Methods:
        music():
            Main group for music commands\n
        join(ctx):
            Joins users channel\n
            ctx (commands.Context) - Context\n
        leave(ctx):
            Leaves channel\n
            ctx (commands.Context) - Context\n
        play(ctx, query):
            Searches YouTube for query, returns top 10 selections, allows user to choose which track, and plays the
            song.\n
            ctx (commands.Context) - Context\n
            query (str) - Query\n
    """

    def __init__(self, bot: DarkBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        on_ready():
            Called when bot is ready to serve content. This confirms that self.bot.user exists.
            Initializes the lavalink client.
        """
        self.bot.musicbackend = lavalink.Client(self.bot.user.id)
        self.bot.musicbackend.add_node("localhost", 2463, "testing", "na", "music-node")
        self.bot.add_listener(
            self.bot.musicbackend.voice_update_handler, "on_socket_response"
        )
        self.bot.musicbackend.add_event_hook(self.track_hook)
        print("Music cog is fully loaded")

    @commands.group()
    async def music(self, ctx):
        pass

    @music.command()
    async def join(self, ctx: commands.Context):
        author = ctx.author
        if ctx.author.voice is not None:
            vc = ctx.author.voice.channel
            player = self.bot.musicbackend.player_manager.create(
                ctx.guild.id, endpoint=str(ctx.guild.region)
            )
            if not player.is_connected:
                player.store("channel", ctx.channel.id)
                await self.connect_to(ctx.guild.id, str(vc.id))

    @music.command()
    async def leave(self, ctx: commands.Context):
        if ctx.author.id not in [544699702558588930, 710669508779573311]:
            await ctx.send(
                "This command is currently hardcoded to only accept starfighter and thepronoobkq"
            )
            return
        await self.connect_to(ctx.guild.id, None)
        await self.bot.musicbackend.player_manager.destroy(ctx.guild.id)

    @music.command()
    async def play(self, ctx: commands.Context, *, query):
        player = self.bot.musicbackend.player_manager.get(ctx.guild.id)
        query = f"ytsearch: {query}"
        results = await player.node.get_tracks(query)
        tracks = results["tracks"][:10]  # We don't want a billion YouTube results
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
        player.add(requester=ctx.author.id, track=track)
        if not player.is_playing:
            await player.play()

    async def connect_to(self, guild_id: int, channel_id: str):
        """
        Connects to the channel\n
        """
        ws = self.bot.connection._get_websocket(
            guild_id
        )  # Not supposed to do, but no clue the proper way to get
        # the WS
        await ws.voice_state(str(guild_id), channel_id)

    async def track_hook(self, event):
        """
        Leaves channel when queue is empty
        """
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)


def setup(bot):
    """
    Setup the cog
    """
    bot.add_cog(Music(bot))
