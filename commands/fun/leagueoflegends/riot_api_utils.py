import aiohttp
import os
import time

_DDRAGON_CACHE = {
    "timestamp": 0,
    "data": None,
    "champion_key_map": {},
    "version": "14.24.1"
}
CACHE_TTL = 3600  # 1 hora de cache

async def fetch_riot_api(url):
    """Faz requisições assíncronas para a Riot API usando a chave de ambiente."""
    api_key = os.getenv("RIOT_API_KEY")
    if not api_key:
        print("[RIOT] RIOT_API_KEY não encontrada no .env")
        return None

    headers = {"X-Riot-Token": api_key}
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            
            print(f"[RIOT] Erro na Riot API: {resp.status} - URL: {url}")
            return None

async def fetch_ddragon_lol_data():
    """Busca campeões, botas e itens atualizados do Data Dragon oficial da Riot em pt_BR com cache."""
    now = time.time()
    if _DDRAGON_CACHE["data"] and (now - _DDRAGON_CACHE["timestamp"] < CACHE_TTL):
        return _DDRAGON_CACHE["data"]

    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # 1. Pega a versão mais recente do patch
            async with session.get("https://ddragon.leagueoflegends.com/api/versions.json") as resp:
                if resp.status != 200:
                    return _DDRAGON_CACHE["data"]
                versions = await resp.json()
                version = versions[0]

            # 2. Pega todos os campeões em pt_BR
            async with session.get(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/pt_BR/champion.json") as resp:
                if resp.status != 200:
                    return _DDRAGON_CACHE["data"]
                champs_json = await resp.json()
                champions = []
                key_map = {}

                for c_id, c in champs_json.get("data", {}).items():
                    champ_info = {
                        "id": c["id"],       # ID para imagem (ex: MonkeyKing, Nunu, Aatrox)
                        "name": c["name"]     # Nome traduzido em pt_BR
                    }
                    champions.append(champ_info)
                    key_map[str(c["key"])] = champ_info

            # 3. Pega todos os itens e botas em pt_BR
            async with session.get(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/pt_BR/item.json") as resp:
                if resp.status != 200:
                    return _DDRAGON_CACHE["data"]
                items_json = await resp.json()
                
                boots = []
                items = []

                for item_id, item in items_json.get("data", {}).items():
                    name = item.get("name", "")
                    tags = item.get("tags", [])
                    gold = item.get("gold", {})
                    maps = item.get("maps", {})
                    purchasable = gold.get("purchasable", False)
                    in_sr = maps.get("11", False)
                    total_cost = gold.get("total", 0)
                    into = item.get("into", [])
                    req_ally = item.get("requiredAlly")
                    req_champ = item.get("requiredChampion")

                    # Ignora itens indisponíveis em Summoner's Rift ou exclusivos de Ornn/específicos
                    if not purchasable or not in_sr or req_ally or req_champ:
                        continue

                    # Botas aprimoradas / Tier 2 (custo >= 900)
                    if "Boots" in tags:
                        if total_cost >= 900:
                            boots.append(name)
                    # Itens lendários / completos finalizados (custo >= 2200 e não evoluem para outro)
                    elif "Consumable" not in tags and "Trinket" not in tags and "GoldPer" not in tags:
                        if not into and total_cost >= 2200:
                            items.append(name)

            data = {
                "version": version,
                "champions": sorted(champions, key=lambda x: x["name"]),
                "boots": sorted(list(set(boots))),
                "items": sorted(list(set(items)))
            }

            _DDRAGON_CACHE["data"] = data
            _DDRAGON_CACHE["champion_key_map"] = key_map
            _DDRAGON_CACHE["version"] = version
            _DDRAGON_CACHE["timestamp"] = now
            print(f"[DDRAGON] Dados do LoL atualizados para o patch {version} ({len(champions)} campeoes, {len(boots)} botas, {len(items)} itens).")
            return data

    except Exception as e:
        print(f"[DDRAGON] Erro ao carregar dados do Data Dragon: {e}")
        return _DDRAGON_CACHE["data"]

async def get_champion_by_key(key: int or str):
    """Retorna o nome e ID do campeão a partir do ID numérico da Riot (ex: 555 -> Pyke)."""
    await fetch_ddragon_lol_data()
    return _DDRAGON_CACHE["champion_key_map"].get(str(key), {"id": "Unknown", "name": f"Campeão #{key}"})

async def get_ddragon_version():
    """Retorna a versão atual do patch do LoL."""
    await fetch_ddragon_lol_data()
    return _DDRAGON_CACHE.get("version", "15.1.1")

_CHAMP_DETAIL_CACHE = {}

async def fetch_champion_detail(champ_id: str):
    """Busca os detalhes completos de um campeão específico (incluindo enemytips) em pt_BR."""
    if champ_id in _CHAMP_DETAIL_CACHE:
        return _CHAMP_DETAIL_CACHE[champ_id]

    version = await get_ddragon_version()
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/pt_BR/champion/{champ_id}.json"

    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    detail = data.get("data", {}).get(champ_id, {})
                    if detail:
                        _CHAMP_DETAIL_CACHE[champ_id] = detail
                    return detail
                print(f"[DDRAGON] Erro ao buscar detalhes de {champ_id}: status {resp.status}")
                return None
    except Exception as e:
        print(f"[DDRAGON] Falha ao requisitar detalhes do campeão {champ_id}: {e}")
        return None