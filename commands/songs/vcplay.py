import discord
import os
import asyncio
from generalFunctions import extract_info, download_single_song, convert_mp3_ytdlp, ytdlp, BASE_DOWNLOAD_FOLDER

song_queues = {}

def setup_vc_commands(bot):

    async def safe_delete(file_path):
        await asyncio.sleep(2)
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Aviso ao deletar arquivo temporario {file_path}: {e}")

    async def play_next(ctx):
        guild_id = ctx.guild.id
        if guild_id not in song_queues or not song_queues[guild_id]['queue']:
            if guild_id in song_queues:
                song_queues[guild_id]['current'] = None
            return

        next_song = song_queues[guild_id]['queue'].pop(0)
        song_queues[guild_id]['current'] = next_song
        next_song['start_time'] = bot.loop.time()

        def after_playing(error):
            if error:
                print(f"[AUDIO] Erro no player FFmpeg: {error}")
            bot.loop.create_task(safe_delete(next_song['file']))
            bot.loop.create_task(play_next(ctx))

        vc = ctx.voice_client
        if vc and vc.is_connected():
            vc.play(discord.FFmpegPCMAudio(next_song['file']), after=after_playing)
            await ctx.send(f"Tocando agora: **{next_song['title']}**")
        else:
            await safe_delete(next_song['file'])
            if guild_id in song_queues:
                song_queues[guild_id]['current'] = None

    @bot.hybrid_command(name="play", aliases=["p"], description="Toca uma música ou playlist do YouTube no canal de voz")
    async def play(ctx, *, url: str):
        voice_state = ctx.author.voice
        if not voice_state:
            return await ctx.send("❌ Entra numa call aí primeiro!", ephemeral=True)

        channel = voice_state.channel
        await ctx.defer()
        
        try:
            vc = ctx.voice_client
            if not vc:
                vc = await channel.connect(timeout=20.0, reconnect=True)
            elif not vc.is_connected():
                await vc.disconnect(force=True)
                vc = await channel.connect(timeout=20.0, reconnect=True)
            elif vc.channel.id != channel.id:
                await vc.move_to(channel)
        except Exception as e:
            return await ctx.send(f"❌ Deu ruim ao conectar na call: {e}")

        vcsongs_path = os.path.join(BASE_DOWNLOAD_FOLDER, str(ctx.guild.id), "vcsongs")

        ydl_opts = {
            'noplaylist': False,
            'concurrent_fragment_downloads': 2,
            'extract_flat': 'in_playlist', 
            'ratelimit': 3145728, 
            'nocheckcertificate': True,
            'default_search': 'ytsearch', 
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'remote_components': 'ejs:github', 
                    'player_client': ['ios', 'web', 'android'],
                }
            }
        }

        convert_mp3_ytdlp(ydl_opts)
        
        queries = [q.strip() for q in url.split(",") if q.strip()]
        
        for query in queries:
            try:
                if ctx.guild.id not in song_queues:
                    song_queues[ctx.guild.id] = {'queue': [], 'current': None}

                info = await extract_info(query, ydl_opts)
                
                if 'entries' in info:
                    entries = list(info['entries'])
                    total_musicas = len(entries)
                    await ctx.send(f"⏳ Carregando {total_musicas} músicas da playlist...")
                    
                    first = entries.pop(0)
                    try:
                        song_info = await download_single_song(first, ydl_opts, folder=vcsongs_path)
                        final_primeira = song_info['filepath']
                        titulo_primeira = song_info.get('title') or os.path.basename(final_primeira).replace(".mp3", "")
                        duracao_primeira = song_info.get('duration', 0)
                        thumb_primeira = song_info.get('thumbnail', "")
                        song_data = {'title': titulo_primeira, 'file': final_primeira, 'duration': duracao_primeira, 'thumbnail': thumb_primeira}
                        
                        if vc.is_playing() or song_queues[ctx.guild.id]['current']:
                            song_queues[ctx.guild.id]['queue'].append(song_data)
                            await ctx.send(f"➕ Adicionado à fila: **{titulo_primeira}**")
                        else:
                            song_queues[ctx.guild.id]['current'] = song_data
                            song_data['start_time'] = bot.loop.time()
                            def after_p(e):
                                if e:
                                    print(f"[AUDIO] Erro no player FFmpeg: {e}")
                                bot.loop.create_task(safe_delete(final_primeira))
                                bot.loop.create_task(play_next(ctx))
                            vc.play(discord.FFmpegPCMAudio(final_primeira), after=after_p)
                            await ctx.send(f"🎶 Tocando agora: **{titulo_primeira}**")
                    except Exception as e:
                        await ctx.send(f"❌ Erro ao carregar primeira música da playlist: {e}")

                    async def bg_download(remaining_entries):
                        for entry in remaining_entries:
                            if ctx.guild.id not in song_queues:
                                break
                            try:
                                song_info = await download_single_song(entry, ydl_opts, folder=vcsongs_path)
                                p = song_info.get('filepath')
                                if not p or not os.path.exists(p):
                                    continue
                                    
                                t = song_info.get('title') or os.path.basename(p).replace(".mp3", "").replace(".NA", "")
                                d = song_info.get('duration', 0)
                                th = song_info.get('thumbnail', "")
                                song_queues[ctx.guild.id]['queue'].append({'title': t, 'file': p, 'duration': d, 'thumbnail': th})

                                cur_vc = ctx.voice_client
                                if cur_vc and cur_vc.is_connected() and not cur_vc.is_playing() and not song_queues[ctx.guild.id].get('current'):
                                    await play_next(ctx)
                            except Exception as err:
                                print(f"[BG_DOWNLOAD] Erro ao baixar faixa da playlist: {err}")
                    
                    bot.loop.create_task(bg_download(entries))
                else:
                    nome_final = await ytdlp(query, ydl_opts, folder=vcsongs_path)
                    titulo = info.get('title') or os.path.basename(nome_final).replace(".mp3", "")
                    duracao = info.get('duration', 0)
                    thumb = info.get('thumbnail', "")
                    song_data = {'title': titulo, 'file': nome_final, 'duration': duracao, 'thumbnail': thumb}
                    
                    if vc.is_playing() or song_queues[ctx.guild.id]['current']:
                        song_queues[ctx.guild.id]['queue'].append(song_data)
                        await ctx.send(f"➕ Adicionado à fila: **{titulo}**")
                    else:
                        song_queues[ctx.guild.id]['current'] = song_data
                        song_data['start_time'] = bot.loop.time()
                        def after_playing(error):
                            if error:
                                print(f"[AUDIO] Erro no player FFmpeg: {error}")
                            bot.loop.create_task(safe_delete(nome_final))
                            bot.loop.create_task(play_next(ctx))
                        vc.play(discord.FFmpegPCMAudio(nome_final), after=after_playing)
                        await ctx.send(f"🎶 Tocando agora: **{titulo}**")

            except Exception as e:
                await ctx.send(f"❌ Deu ruim: {e}")
                if 'nome_final' in locals() and nome_final and os.path.exists(nome_final):
                    try:
                        os.remove(nome_final)
                    except: pass
