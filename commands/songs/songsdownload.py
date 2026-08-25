import discord, os, asyncio
from generalFunctions import ytdlp, convert_mp3_ytdlp, upload_to_litterbox, BASE_DOWNLOAD_FOLDER

def setup_songs_commands(bot):
    @bot.command(name="baixe", aliases=["instale", "baixar", "download"])
    async def baixe(ctx, formato: str = None, *, url: str = None):
        if not formato or not url:
            await ctx.send(f"Qual o link do que tu quer baixar? Sintaxe: `{ctx.prefix}baixe <mp3/mp4> <url>`")
            return
        
        baixe_path = os.path.join(BASE_DOWNLOAD_FOLDER, str(ctx.guild.id), "baixe")

        ydl_opts = {
            'noplaylist': True,
            'concurrent_fragment_downloads': 2,
            'ratelimit': 3145728,
            'nocheckcertificate': True,
            'default_search': 'ytsearch',
            'extractor_args': {
                'youtube': {
                    'remote_components': 'ejs:github', 
                    'player_client': ['ios', 'web', 'android'],
                }
            }
        }

        nome_final = None
        try:
            if "mp3" in formato.lower():
                convert_mp3_ytdlp(ydl_opts)
                await ctx.send("Baixando e convertendo pra mp3, calma ai um cadin...")
                nome_final = await ytdlp(url, ydl_opts, folder=baixe_path)
            
            elif "mp4" in formato.lower():
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                ydl_opts['merge_output_format'] = 'mp4'
                await ctx.send("Baixando o vídeo em mp4, aguenta ai...")
                nome_final = await ytdlp(url, ydl_opts, folder=baixe_path)

                tamanho_bytes = os.path.getsize(nome_final)
                if tamanho_bytes > 8 * 1024 * 1024:
                    await ctx.send(f"Vídeo muito grande ({tamanho_bytes/(1024*1024):.2f}MB). Fazendo upload para link externo...")
                    link = await upload_to_litterbox(nome_final)
                    if link:
                        await ctx.send(f"Aqui está o link do seu vídeo: {link}")
                    else:
                        await ctx.send("Erro ao fazer upload para link externo.")
                    return
            
            else:
                await ctx.send("Formato inválido. Use `mp3` ou `mp4`.")
                return

            if nome_final and os.path.exists(nome_final):
                await ctx.send(file=discord.File(nome_final))
                
        except Exception as e:
            print(f"Erro detalhado no comando baixe: {e}")
            await ctx.send(f"Erro ao processar: {type(e).__name__}.")
        finally:
            await asyncio.sleep(2)
            if nome_final and os.path.exists(nome_final):
                try:
                    os.remove(nome_final)
                except Exception as err:
                    print(f"Aviso ao remover arquivo temporario: {err}")
