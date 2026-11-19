import discord, os, asyncio
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from discord import app_commands
from utils.youtube import ytdlp, convert_mp3_ytdlp, BASE_DOWNLOAD_FOLDER
from utils.litterbox import upload_to_litterbox
from utils.feedback import processing_feedback


PLAYLIST_PARAMS = ("list", "start_radio", "index")


def clean_playlist_url(url: str):
    """Remove parâmetros de playlist/rádio mantendo apenas o vídeo/áudio principal.

    Retorna (url_limpa, foi_limpo, playlist_pura).
    """
    raw = url.strip()
    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https"):
        return raw, False, False

    qs = parse_qs(parsed.query, keep_blank_values=True)
    if parsed.path.rstrip("/").endswith("/playlist") and "v" not in qs:
        return raw, False, True

    if any(param in qs for param in PLAYLIST_PARAMS):
        for param in PLAYLIST_PARAMS:
            qs.pop(param, None)
        cleaned = urlunparse(parsed._replace(query=urlencode(qs, doseq=True)))
        return cleaned, True, False

    return raw, False, False

def setup_songs_commands(bot):
    @bot.hybrid_command(name="baixe", aliases=["instale", "baixar", "download"], description="Baixa uma música em mp3 ou vídeo em mp4")
    @app_commands.describe(formato="Escolha o formato de download", url="Link ou nome da música/vídeo")
    @app_commands.choices(formato=[
        app_commands.Choice(name="MP3 (Áudio)", value="mp3"),
        app_commands.Choice(name="MP4 (Vídeo)", value="mp4"),
    ])
    async def baixe(ctx, formato: str, *, url: str):
        fmt = formato.lower()
        if "mp3" not in fmt and "mp4" not in fmt:
            return await ctx.send("❌ Formato inválido. Use `mp3` ou `mp4`.", ephemeral=True, delete_after=10)

        url, was_cleaned, is_pure_playlist = clean_playlist_url(url)
        if is_pure_playlist:
            return await ctx.send(
                "❌ Esse link é de uma playlist completa sem um vídeo principal. Envie o link direto de uma música ou vídeo!",
                ephemeral=True,
                delete_after=10,
            )

        await ctx.defer()
        if was_cleaned:
            await ctx.send(
                "ℹ️ Link de playlist/rádio detectado — limpei a URL para baixar apenas o arquivo principal.",
                delete_after=10,
            )
        
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
            async with processing_feedback(ctx, "⏳ Baixando e processando mídia...") as status:
                if "mp3" in fmt:
                    convert_mp3_ytdlp(ydl_opts)
                    nome_final = await ytdlp(url, ydl_opts, folder=baixe_path)
                else:
                    ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                    ydl_opts['merge_output_format'] = 'mp4'
                    nome_final = await ytdlp(url, ydl_opts, folder=baixe_path)

                    tamanho_bytes = os.path.getsize(nome_final)
                    if tamanho_bytes > 8 * 1024 * 1024:
                        await status.update("☁️ Arquivo maior que 8MB, enviando para o Litterbox...")
                        link = await upload_to_litterbox(nome_final)
                        if link:
                            await ctx.send(f"📦 Vídeo muito grande ({tamanho_bytes/(1024*1024):.2f}MB). Link para download: {link}")
                        else:
                            await ctx.send("❌ Erro ao fazer upload para link externo.", delete_after=10)
                        return

                if nome_final and os.path.exists(nome_final):
                    await status.update("📤 Enviando arquivo...")
                    await ctx.send(file=discord.File(nome_final))
                
        except Exception as e:
            print(f"Erro detalhado no comando baixe: {e}")
            await ctx.send(f"❌ Erro ao processar: {type(e).__name__}.", delete_after=10)
        finally:
            await asyncio.sleep(2)
            if nome_final and os.path.exists(nome_final):
                try:
                    os.remove(nome_final)
                except Exception as err:
                    print(f"Aviso ao remover arquivo temporario: {err}")
