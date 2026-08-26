import discord
from discord.ext import commands
from commands.fun.leagueoflegends.riot_api_utils import fetch_ddragon_lol_data, fetch_champion_detail, get_ddragon_version

# Aliases populares para busca rápida de campeões
CHAMPION_ALIASES = {
    "asol": "AurelionSol",
    "aurelion": "AurelionSol",
    "tf": "TwistedFate",
    "twisted": "TwistedFate",
    "kata": "Katarina",
    "mf": "MissFortune",
    "miss": "MissFortune",
    "ww": "Warwick",
    "yi": "MasterYi",
    "master": "MasterYi",
    "mundo": "DrMundo",
    "dr mundo": "DrMundo",
    "drmundo": "DrMundo",
    "nunu": "Nunu",
    "willump": "Nunu",
    "jarvan": "JarvanIV",
    "j4": "JarvanIV",
    "ksante": "KSante",
    "k'sante": "KSante",
    "chogath": "Chogath",
    "cho'gath": "Chogath",
    "kaisa": "Kaisa",
    "kai'sa": "Kaisa",
    "khazix": "Khazix",
    "kha'zix": "Khazix",
    "kogmaw": "KogMaw",
    "kog'maw": "KogMaw",
    "reksai": "RekSai",
    "rek'sai": "RekSai",
    "velkoz": "Velkoz",
    "vel'koz": "Velkoz",
    "wukong": "MonkeyKing",
    "macaco": "MonkeyKing",
    "xin": "XinZhao",
    "xinzhao": "XinZhao",
    "cait": "Caitlyn",
    "cass": "Cassiopeia",
    "gp": "Gangplank",
    "hecarim": "Hecarim",
    "morde": "Mordekaiser",
    "tahm": "TahmKench",
    "kench": "TahmKench",
    "tk": "TahmKench",
    "vlad": "Vladimir",
}

TAG_TRANSLATIONS = {
    "Fighter": "Lutador",
    "Mage": "Mago",
    "Assassin": "Assassino",
    "Tank": "Tanque",
    "Marksman": "Atirador",
    "Support": "Suporte",
}

def setup_counter_command(bot):
    @bot.hybrid_command(
        name="counter",
        aliases=["counters", "contra"],
        description="Mostra dicas de como jogar contra e counterar um campeão de LoL"
    )
    async def counter(ctx, *, campeao: str):
        await ctx.defer()

        clean_query = campeao.strip().lower().replace(" ", "").replace("'", "").replace(".", "")
        lol_data = await fetch_ddragon_lol_data()
        if not lol_data:
            return await ctx.send("❌ Erro ao conectar com o Data Dragon da Riot Games.")

        champions = lol_data["champions"]

        # 1. Busca por alias pré-definido
        target_id = CHAMPION_ALIASES.get(campeao.strip().lower()) or CHAMPION_ALIASES.get(clean_query)
        matched = None

        if target_id:
            matched = next((c for c in champions if c["id"].lower() == target_id.lower()), None)

        # 2. Busca exata por nome ou ID
        if not matched:
            for c in champions:
                c_name_clean = c["name"].lower().replace(" ", "").replace("'", "").replace(".", "")
                c_id_clean = c["id"].lower().replace(" ", "").replace("'", "").replace(".", "")
                if clean_query == c_name_clean or clean_query == c_id_clean:
                    matched = c
                    break

        # 3. Busca por substring
        if not matched:
            for c in champions:
                if clean_query in c["name"].lower() or clean_query in c["id"].lower():
                    matched = c
                    break

        if not matched:
            return await ctx.send(f"❌ Campeão `{campeao}` não encontrado. Verifique o nome e tente novamente.")

        champ_id = matched["id"]
        champ_name = matched["name"]

        # Busca detalhes completos do campeão (incluindo enemytips)
        detail = await fetch_champion_detail(champ_id)
        if not detail:
            return await ctx.send(f"❌ Erro ao buscar detalhes de `{champ_name}` no Data Dragon.")

        enemy_tips = detail.get("enemytips", [])
        title = detail.get("title", "")
        tags = [TAG_TRANSLATIONS.get(t, t) for t in detail.get("tags", [])]
        tags_str = ", ".join(tags) if tags else "N/A"

        patch_version = await get_ddragon_version()

        embed = discord.Embed(
            title=f"🛡️ Como Counterar: {champ_name} ({title.capitalize()})",
            color=discord.Color.red()
        )

        loading_img = f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champ_id}_0.jpg"
        embed.set_thumbnail(url=loading_img)
        embed.add_field(name="🏷️ Classe / Função", value=f"`{tags_str}`", inline=True)

        # Dicas oficiais de contra-ataque
        if enemy_tips:
            tips_text = "\n\n".join([f"🔹 {tip}" for tip in enemy_tips])
            embed.add_field(name="🎯 Dicas Táticas de Confronto", value=tips_text, inline=False)
        else:
            embed.add_field(
                name="🎯 Dicas Táticas",
                value="• Mantenha a visão das rotas de flanco.\n• Guarde habilidades de controle de grupo (CC) para momentos decisivos.",
                inline=False
            )

        # Links para estatísticas e matchups
        opgg_url = f"https://www.op.gg/champions/{champ_id.lower()}/counters"
        ugg_url = f"https://u.gg/lol/champions/{champ_id.lower()}/counter"
        embed.add_field(
            name="📊 Matchups e Estatísticas ao Vivo",
            value=f"[Ver counters no OP.GG]({opgg_url}) • [Ver counters no U.GG]({ugg_url})",
            inline=False
        )

        embed.set_footer(text=f"Patch {patch_version} • Solicitado por {ctx.author.display_name}")
        await ctx.send(embed=embed)
