import os
import random
import string
import aiohttp


async def upload_to_litterbox(file_path):
    """Faz upload para o Litterbox com expiração de 12 horas e nome aleatório."""
    url = "https://litterbox.catbox.moe/resources/internals/api.php"
    if not os.path.exists(file_path):
        return None

    try:
        extension = os.path.splitext(file_path)[1]
        random_name = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16)) + extension

        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('reqtype', 'fileupload')
                data.add_field('time', '12h')  # Expira em 12 horas
                data.add_field('fileToUpload', f, filename=random_name)

                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        return await response.text()
    except Exception as e:
        print(f"Erro no upload para o Litterbox: {e}")
    return None
