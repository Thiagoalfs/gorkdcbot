import os
import random
import string
import aiohttp

LITTERBOX_URL = "https://litterbox.catbox.moe/resources/internals/api.php"
TMPFILES_URL = "https://tmpfiles.org/api/v1/upload"
UPLOAD_TIMEOUT = aiohttp.ClientTimeout(total=180)


async def _upload_litterbox(session: aiohttp.ClientSession, file_path: str, random_name: str):
    with open(file_path, "rb") as f:
        data = aiohttp.FormData()
        data.add_field("reqtype", "fileupload")
        data.add_field("time", "12h")  # Expira em 12 horas
        data.add_field("fileToUpload", f, filename=random_name)

        async with session.post(LITTERBOX_URL, data=data) as response:
            body = (await response.text()).strip()
            if response.status == 200 and body.startswith("http"):
                return body
            print(f"[UPLOAD] Litterbox falhou (HTTP {response.status}): {body[:200]}")
    return None


async def _upload_tmpfiles(session: aiohttp.ClientSession, file_path: str, random_name: str):
    with open(file_path, "rb") as f:
        data = aiohttp.FormData()
        data.add_field("file", f, filename=random_name)

        async with session.post(TMPFILES_URL, data=data) as response:
            if response.status == 200:
                payload = await response.json()
                url = payload.get("data", {}).get("url")
                if url:
                    return url
            body = await response.text()
            print(f"[UPLOAD] tmpfiles.org falhou (HTTP {response.status}): {body[:200]}")
    return None


async def upload_to_litterbox(file_path):
    """Faz upload para o Litterbox (12h) com fallback automático para tmpfiles.org."""
    if not os.path.exists(file_path):
        return None

    extension = os.path.splitext(file_path)[1]
    random_name = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(16)) + extension

    async with aiohttp.ClientSession(timeout=UPLOAD_TIMEOUT) as session:
        try:
            link = await _upload_litterbox(session, file_path, random_name)
            if link:
                return link
        except Exception as e:
            print(f"[UPLOAD] Erro no upload para o Litterbox: {e}")

        try:
            link = await _upload_tmpfiles(session, file_path, random_name)
            if link:
                return link
        except Exception as e:
            print(f"[UPLOAD] Erro no upload para o tmpfiles.org: {e}")

    return None
