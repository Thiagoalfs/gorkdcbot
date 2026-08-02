import discord
import nacl
import os, json
import asyncio, yt_dlp
from commands.languageservice import languageservice
from generalFunctions import extract_info, download_single_song, convert_mp3_ytdlp, ytdlp

# Dicionário global para gerenciar a fila e o estado de cada servidor
# Estrutura: { guild_id: { 'queue': [], 'current': None } }
song_queues = {}

def setup_vc_commands(bot):

    async def safe_delete(file_path):
        """Tenta deletar o arquivo após um delay para o Windows liberar o handle do FFmpeg."""
        await asyncio.sleep(2)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Erro ao deletar arquivo temporário {file_path}: {e}")

    async def play_next(ctx):
        responses = await languageservice(bot, ctx, "songs", "vcplay.json")

        if ctx.guild.id not in song_queues or not song_queues[ctx.guild.id]['queue']:
            song_queues[ctx.guild.id]['current'] = None
            return

        # Pega a próxima música da fila
        next_song = song_queues[ctx.guild.id]['queue'].pop(0)
        song_queues[ctx.guild.id]['current'] = next_song
        next_song['start_time'] = bot.loop.time()

        def after_playing(error):
            bot.loop.create_task(safe_delete(next_song['file']))
            # Chama a próxima música
            bot.loop.create_task(play_next(ctx))

        vc = ctx.voice_client
        # Ensure vc is still connected before trying to play
        if vc:
            vc.play(discord.FFmpegPCMAudio(next_song['file']), after=after_playing)
            await ctx.send(f"{responses['playing']} **{next_song['title']}**")

    @bot.command(name="play", aliases=["p"])
    async def play(ctx, *, url: str = None):
        responses = await languageservice(bot, ctx, "songs", "vcplay.json")
        
        if not url:
            await ctx.send(responses['no_url'])
            return

        voice_state = ctx.author.voice
        if not voice_state:
            await ctx.send(responses['no_vc'])
            return

        channel = voice_state.channel
        
        # Lógica de join refatorada para evitar travamentos (Timeout e Reconnect)
        try:
            if ctx.voice_client:
                if ctx.voice_client.channel.id != channel.id:
                    await ctx.voice_client.move_to(channel)
                vc = ctx.voice_client
            else:
                vc = await channel.connect(timeout=20.0, reconnect=True)
        except Exception as e:
            return await ctx.send(responses['joining_error'])

        vcsongs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "downloadedsongs", str(ctx.guild.id), "vcsongs")

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

        # Configura para áudio/mp3
        convert_mp3_ytdlp(ydl_opts)
        
        # Divide a entrada por vírgulas para suportar múltiplos pedidos de uma vez
        queries = [q.strip() for q in url.split(",") if q.strip()]
        
        for query in queries:
            try:
                # Inicializa a fila do servidor se não existir
                if ctx.guild.id not in song_queues:
                    song_queues[ctx.guild.id] = {'queue': [], 'current': None}

                # Extrai informações primeiro para ver se é playlist ou música única
                info = await extract_info(query, ydl_opts)
                
                if 'entries' in info:
                    # É uma playlist ou resultado de busca múltipla
                    entries = list(info['entries'])
                    total_musicas = len(entries)
                    msg_loading = await ctx.send(f"{responses['msg_loading1']} {total_musicas} {responses['msg_loading2']}")
                    
                    # Baixa e toca a primeira música imediatamente
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
                            await ctx.send(f"{responses['added_to_queue']} **{titulo_primeira}**")
                        else:
                            song_queues[ctx.guild.id]['current'] = song_data
                            song_data['start_time'] = bot.loop.time()
                            def after_p(e):
                                bot.loop.create_task(safe_delete(final_primeira))
                                bot.loop.create_task(play_next(ctx))
                            vc.play(discord.FFmpegPCMAudio(final_primeira), after=after_p)
                            await ctx.send(f"{responses['playing']}**{titulo_primeira}**")
                        
                        # Deleta a mensagem de carregamento da playlist
                        try:
                            await msg_loading.delete()
                        except: pass
                    except Exception as e:
                        await ctx.send(f"{responses['joining_error']}")

                    # O restante baixa em segundo plano
                    async def bg_download(remaining_entries):
                        for entry in remaining_entries:
                            # Verifica se o bot ainda está no servidor/fila existe
                            if ctx.guild.id not in song_queues:
                                break
                            try:
                                song_info = await download_single_song(entry, ydl_opts, folder=vcsongs_path)
                                p = song_info['filepath']
                                # Se p for None ou algo deu errado no download, pula
                                if not p or not os.path.exists(p):
                                    continue
                                    
                                t = song_info.get('title') or os.path.basename(p).replace(".mp3", "").replace(".NA", "")
                                d = song_info.get('duration', 0)
                                th = song_info.get('thumbnail', "")
                                song_queues[ctx.guild.id]['queue'].append({'title': t, 'file': p, 'duration': d, 'thumbnail': th})
                            except: pass
                    
                    bot.loop.create_task(bg_download(entries))
                else:
                    # Música única
                    msg_loading = await ctx.send(f"carregando música...", reference=ctx.message)
                    nome_final = await ytdlp(query, ydl_opts, folder=vcsongs_path)
                    titulo = info.get('title') or os.path.basename(nome_final).replace(".mp3", "")
                    duracao = info.get('duration', 0)
                    thumb = info.get('thumbnail', "")
                    song_data = {'title': titulo, 'file': nome_final, 'duration': duracao, 'thumbnail': thumb}
                    
                    if vc.is_playing() or song_queues[ctx.guild.id]['current']:
                        song_queues[ctx.guild.id]['queue'].append(song_data)
                        await ctx.send(f"adicionado à fila: **{titulo}**")
                    else:
                        song_queues[ctx.guild.id]['current'] = song_data
                        song_data['start_time'] = bot.loop.time()
                        def after_playing(error):
                            bot.loop.create_task(safe_delete(nome_final))
                            bot.loop.create_task(play_next(ctx))
                        vc.play(discord.FFmpegPCMAudio(nome_final), after=after_playing)
                        await ctx.send(f"{responses['playing']}**{titulo}**")
                    
                    # Deleta a mensagem de carregamento da busca única
                    try:
                        await msg_loading.delete()
                    except: pass

            except Exception as e:
                await ctx.send(f"{responses['joining_error']}")
                if 'nome_final' in locals() and os.path.exists(nome_final):
                    os.remove(nome_final)
