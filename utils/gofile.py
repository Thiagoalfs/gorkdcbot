import os
import random
import string
import aiohttp

UGUU_UPLOAD_URL = "https://uguu.se/upload"
UGUU_MAX_BYTES = 128 * 1024 * 1024  # 128 MB
GOFILE_UPLOAD_URL = "https://upload.gofile.io/uploadfile"
TMPFILES_URL = "https://tmpfiles.org/api/v1/upload"
UPLOAD_TIMEOUT = aiohttp.ClientTimeout(total=180)


async def _upload_uguu(session: aiohttp.ClientSession, file_path: str, random_name: str):
    with open(file_path, "rb") as f:
        data = aiohttp.FormData()
        data.add_field("files[]", f, filename=random_name)

        async with session.post(UGUU_UPLOAD_URL, data=data) as response:
            if response.status == 200:
                payload = await response.json()
                files = payload.get("files") or []
                if payload.get("success") and files and files[0].get("url"):
                    return files[0]["url"]
            body = await response.text()
            print(f"[UPLOAD] uguu.se falhou (HTTP {response.status}): {body[:200]}")
    return None


async def _upload_gofile(session: aiohttp.ClientSession, file_path: str, random_name: str):
    with open(file_path, "rb") as f:
        data = aiohttp.FormData()
        data.add_field("file", f, filename=random_name)

        async with session.post(GOFILE_UPLOAD_URL, data=data) as response:
            if response.status == 200:
                payload = await response.json()
                if payload.get("status") == "ok":
                    download_page = payload.get("data", {}).get("downloadPage")
                    if download_page:
                        return download_page
            body = await response.text()
            print(f"[UPLOAD] Gofile falhou (HTTP {response.status}): {body[:200]}")
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


async def upload_to_gofile(file_path):
    """Envia para uguu.se (<= 128MB, link direto com player no Discord) ou Gofile.io (> 128MB/fallback), com fallback final para tmpfiles.org."""
    if not os.path.exists(file_path):
        return None

    file_size = os.path.getsize(file_path)
    extension = os.path.splitext(file_path)[1]
    random_name = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(16)) + extension

    async with aiohttp.ClientSession(timeout=UPLOAD_TIMEOUT) as session:
        if file_size <= UGUU_MAX_BYTES:
            try:
                link = await _upload_uguu(session, file_path, random_name)
                if link:
                    return link
            except Exception as e:
                print(f"[UPLOAD] Erro no upload para o uguu.se: {e}")

        try:
            link = await _upload_gofile(session, file_path, random_name)
            if link:
                return link
        except Exception as e:
            print(f"[UPLOAD] Erro no upload para o Gofile: {e}")

        try:
            link = await _upload_tmpfiles(session, file_path, random_name)
            if link:
                return link
        except Exception as e:
            print(f"[UPLOAD] Erro no upload para o tmpfiles.org: {e}")

    return None
