from discord.ext import commands
from commands.songs.songsdownload import setup_songs_commands
from commands.songs.vcplay import setup_vc_commands
from commands.songs.skip import setup_skip_command
from commands.songs.queue import setup_queue_command
from commands.songs.stop import setup_stop_command
from commands.songs.nowplaying import setup_nowplaying_command
from commands.user.useravatar import useravatar
from commands.user.userinfo import userinfo
from commands.misc.ping import ping
from commands.misc.help import help
from commands.server.servericon import server_icon
from commands.server.serverinfo import server_info
from commands.fun.coinflip import coin_flip
from commands.fun.leagueoflegends.lolgen import setup_lolgen_command
from commands.fun.leagueoflegends.league_link import setup_league_link_command
from commands.fun.leagueoflegends.league_info import setup_league_info_command
from commands.admin.prefix import setup_prefix_command
from commands.admin.clear import setup_clear_command
from commands.admin.ban import setup_ban_command
from commands.admin.kick import setup_kick_command
from commands.admin.unban import setup_unban_command
from commands.admin.language import setup_language_command
from commands.admin.config import setup_config_command
from commands.fun.gambling import setup_gambling_command






def setup_commands(bot):

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"Esse comando não existe. Digite `{ctx.prefix}help` para ver a lista de comandos.", delete_after=5)

    #songs related commands
    setup_vc_commands(bot)
    setup_songs_commands(bot)
    setup_skip_command(bot)
    setup_stop_command(bot)
    setup_queue_command(bot)
    setup_nowplaying_command(bot)

    #user commands
    useravatar(bot)
    userinfo(bot)

    #misc
    ping(bot)
    help(bot)
    coin_flip(bot)
    setup_lolgen_command(bot)
    setup_league_link_command(bot)
    setup_league_info_command(bot)

    #admin
    setup_prefix_command(bot)
    setup_clear_command(bot)
    setup_ban_command(bot)
    setup_kick_command(bot)
    setup_unban_command(bot)
    setup_language_command(bot)
    setup_config_command(bot)

    #fun
    setup_gambling_command(bot)
    
    #server
    server_icon(bot)
    server_info(bot)