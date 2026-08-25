import discord, random, yt_dlp, asyncio, os, aiohttp, string

BASE_DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloadedsongs")
    
def convert_mp3_ytdlp(ydl_opts):
    ydl_opts.update({
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    })

async def extract_info(url, ydl_opts):
    """Extracts information about a video or playlist without downloading."""
    loop = asyncio.get_event_loop()
    def _run():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    return await loop.run_in_executor(None, _run)

async def ytdlp(videourl, ydl_opts, folder=None):
    folder = folder or BASE_DOWNLOAD_FOLDER
    os.makedirs(folder, exist_ok=True)
    download_opts = ydl_opts.copy()
    download_opts['outtmpl'] = f'{folder}/%(title)s.%(ext)s'
    download_opts.pop('extract_flat', None) # Garante que aqui ele pegue os dados reais
    loop = asyncio.get_event_loop()
    def _run():
        with yt_dlp.YoutubeDL(download_opts) as ydl:
            info = ydl.extract_info(videourl, download=True)
            
            # Se for um resultado de busca, os dados do download estão na primeira entrada
            if 'entries' in info and info['entries']:
                info = info['entries'][0]

            # Prioriza o caminho real do arquivo gerado pelo yt-dlp
            if 'filepath' in info:
                return info['filepath']
            
            # Fallback: reconstrói o nome e corrige a extensão se houver conversão para mp3
            filename = ydl.prepare_filename(info)
            if any(pp.get('key') == 'FFmpegExtractAudio' for pp in download_opts.get('postprocessors', [])):
                filename = os.path.splitext(filename)[0] + ".mp3"
            return filename
    return await loop.run_in_executor(None, _run)

async def download_single_song(info_dict, ydl_opts, folder=None):
    """Downloads a single song given its info dictionary."""
    folder = folder or BASE_DOWNLOAD_FOLDER
    os.makedirs(folder, exist_ok=True)
    # Ensure 'outtmpl' is set for the download
    download_ydl_opts = ydl_opts.copy()
    download_ydl_opts['outtmpl'] = f'{folder}/%(title)s.%(ext)s'
    download_ydl_opts.pop('extract_flat', None) # Queremos info completa aqui
    # Ensure no playlist processing for single download
    download_ydl_opts['noplaylist'] = True

    loop = asyncio.get_event_loop()
    def _run():
        with yt_dlp.YoutubeDL(download_ydl_opts) as ydl:
            # Baixa e retorna a info atualizada (que contém o filepath após o download)
            url = info_dict.get('webpage_url') or info_dict.get('url')
            info = ydl.extract_info(url, download=True)

            if 'entries' in info and info['entries']:
                info = info['entries'][0]
            
            if 'filepath' in info:
                pass
            else:
                filename = ydl.prepare_filename(info)
                if any(pp.get('key') == 'FFmpegExtractAudio' for pp in download_ydl_opts.get('postprocessors', [])):
                    filename = os.path.splitext(filename)[0] + ".mp3"
                info['filepath'] = filename
            
            return info # Agora retorna o dicionário completo com metadados e caminho
    return await loop.run_in_executor(None, _run)

async def upload_to_litterbox(file_path):
    """Faz upload para o Litterbox com expiração de 1 hora e nome aleatório."""
    url = "https://litterbox.catbox.moe/resources/internals/api.php"
    if not os.path.exists(file_path):
        return None

    try:
        # Gera um nome de arquivo aleatório de 16 caracteres + extensão original
        extension = os.path.splitext(file_path)[1]
        random_name = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16)) + extension

        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('reqtype', 'fileupload')
                data.add_field('time', '1h') # Expira em 1 hora
                data.add_field('fileToUpload', f, filename=random_name)
                
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        return await response.text()
    except Exception as e:
        print(f"Erro no upload para o Litterbox: {e}")
    return None
