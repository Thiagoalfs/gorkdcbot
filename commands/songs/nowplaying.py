import discord
from commands.songs.vcplay import song_queues

def setup_nowplaying_command(bot):
    def format_time(seconds):
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f'{h:d}:{m:02d}:{s:02d}'
        return f'{m:02d}:{s:02d}'

    def create_progress_bar(current, total, size=15):
        if total <= 0: return "🔘" + "▬" * (size - 1)
        percentage = current / total
        progress = int(size * percentage)
        progress = min(max(progress, 0), size - 1)
        bar = "▬" * progress + "🔘" + "▬" * (size - progress - 1)
        return bar

    @bot.command(name="nowplaying", aliases=["np", "tocando"])
    async def nowplaying(ctx):
        state = song_queues.get(ctx.guild.id)
        
        if not state or not state['current']:
            return await ctx.send("Não tô tocando nada agora. Usa !play.")
        
        if not ctx.voice_client or not ctx.voice_client.is_playing():
             return await ctx.send("O som tá pausado ou bugou, ze.")

        current = state['current']
        
        start_time = current.get('start_time', bot.loop.time())
        duration = current.get('duration', 0)
        elapsed = bot.loop.time() - start_time
        
        time_str = f"{format_time(elapsed)} / {format_time(duration)}"
        progress_bar = create_progress_bar(elapsed, duration)

        embed = discord.Embed(
            title="🎵 Tocando Agora",
            description=f"**{current['title']}**\n\n{progress_bar}\n`{time_str}`",
            color=discord.Color.blue()
        )
        
        if current.get('thumbnail'):
            embed.set_thumbnail(url=current['thumbnail'])
        
        embed.set_footer(text=f"Pedido por: {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
