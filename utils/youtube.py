import asyncio
import os
import yt_dlp

BASE_DOWNLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "downloadedsongs",
)


def convert_mp3_ytdlp(ydl_opts):
    ydl_opts.update({
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    })


def _resolve_filepath(ydl, info, download_opts):
    if 'entries' in info and info['entries']:
        info = info['entries'][0]

    if 'filepath' in info:
        return info, info['filepath']

    filename = ydl.prepare_filename(info)
    if any(pp.get('key') == 'FFmpegExtractAudio' for pp in download_opts.get('postprocessors', [])):
        filename = os.path.splitext(filename)[0] + ".mp3"
    return info, filename


async def extract_info(url, ydl_opts):
    """Extracts information about a video or playlist without downloading."""
    loop = asyncio.get_running_loop()

    def _run():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    return await loop.run_in_executor(None, _run)


def _prepare_download_opts(ydl_opts, folder, single=False):
    folder = folder or BASE_DOWNLOAD_FOLDER
    os.makedirs(folder, exist_ok=True)
    opts = ydl_opts.copy()
    opts['outtmpl'] = f'{folder}/%(title)s [%(id)s].%(ext)s'
    opts.pop('extract_flat', None)  # Garante dados reais no download
    if single:
        opts['noplaylist'] = True
    return opts


async def ytdlp(videourl, ydl_opts, folder=None):
    download_opts = _prepare_download_opts(ydl_opts, folder)
    loop = asyncio.get_running_loop()

    def _run():
        with yt_dlp.YoutubeDL(download_opts) as ydl:
            info = ydl.extract_info(videourl, download=True)
            _, filepath = _resolve_filepath(ydl, info, download_opts)
            return filepath

    return await loop.run_in_executor(None, _run)


async def download_single_song(info_dict, ydl_opts, folder=None):
    """Downloads a single song given its info dictionary."""
    download_ydl_opts = _prepare_download_opts(ydl_opts, folder, single=True)
    loop = asyncio.get_running_loop()

    def _run():
        with yt_dlp.YoutubeDL(download_ydl_opts) as ydl:
            url = info_dict.get('webpage_url') or info_dict.get('url')
            info = ydl.extract_info(url, download=True)
            info, filepath = _resolve_filepath(ydl, info, download_ydl_opts)
            info['filepath'] = filepath
            return info  # Agora retorna o dicionário completo com metadados e caminho

    return await loop.run_in_executor(None, _run)
