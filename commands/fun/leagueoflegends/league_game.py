import discord
from discord.ext import commands
from urllib.parse import quote
import time
from commands.fun.leagueoflegends.riot_api_utils import fetch_riot_api, get_champion_by_key, get_ddragon_version

QUEUE_TYPES = {
    400: "Normal Alternada",
    420: "Ranqueada Solo/Duo",
    430: "Normal Escolha às Cegas",
    440: "Ranqueada Flex",
    450: "ARAM",
    490: "Quickplay",
    700: "Clash",
    1700: "Arena (2v2v2v2)",
    1900: "URF",
}

def setup_league_game_command(bot):
    @bot.hybrid_command(
        name="lolgame",
        aliases=["partida", "game", "livegame", "ingame"],
        description="Mostra informações da partida ao vivo de um jogador de LoL"
    )
    async def lolgame(ctx, *, usuario: str = None):
        await ctx.defer()

        riot_id = None
        target_member = None

        # 1. Verifica se foi mencionada uma pessoa ou passado um Riot ID
        if ctx.message and ctx.message.mentions:
            target_member = ctx.message.mentions[0]
        elif usuario:
            clean_str = usuario.strip("<@!> ")
            if clean_str.isdigit():
                target_member = ctx.guild.get_member(int(clean_str)) if ctx.guild else None
            elif "#" in usuario:
                riot_id = usuario.strip()

        # 2. Se não passou Riot ID explicitamente, busca no banco vinculado
        if not riot_id:
            target_member = target_member or ctx.author
            data = await bot.db.fetch_one("SELECT riot_id FROM leagueconfig WHERE user_id = %s", (target_member.id,))
            if not data:
                if target_member == ctx.author:
                    return await ctx.send("❌ Você não vinculou uma conta. Use `/leaguelink Nome#TAG` ou informe: `/lolgame Nome#TAG`.")
                else:
                    return await ctx.send(f"❌ **{target_member.display_name}** não vinculou uma conta no bot.")
            riot_id = data['riot_id']

        if "#" not in riot_id:
            return await ctx.send("❌ Formato de Riot ID inválido. Use `Nome#TAG`.")

        name, tag = riot_id.rsplit("#", 1)
        name_encoded, tag_encoded = quote(name), quote(tag)

        # 3. Busca PUUID
        acc_data = await fetch_riot_api(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name_encoded}/{tag_encoded}")
        if not acc_data:
            return await ctx.send(f"❌ Conta `{riot_id}` não encontrada na Riot Games.")
        puuid = acc_data['puuid']

        # 4. Busca partida ativa no Spectator V5
        game_data = await fetch_riot_api(f"https://br1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}")
        if not game_data:
            return await ctx.send(f"❌ **{riot_id}** não está em nenhuma partida ativa no momento.")

        queue_id = game_data.get('gameQueueConfigId', 0)
        queue_name = QUEUE_TYPES.get(queue_id, game_data.get('gameMode', 'Personalizada'))

        # 5. Calcula tempo de partida
        game_length = game_data.get('gameLength', 0)
        game_start_time = game_data.get('gameStartTime', 0)
        if game_start_time > 0 and game_length <= 0:
            game_length = int(time.time() - (game_start_time / 1000))

        mins, secs = divmod(max(0, game_length), 60)
        time_str = f"{mins:02d}:{secs:02d}"

        blue_team = []
        red_team = []

        for p in game_data.get('participants', []):
            champ_id = p.get('championId', 0)
            champ_info = await get_champion_by_key(champ_id)
            p_riot_id = p.get('riotId') or p.get('summonerName') or "Invocador"

            is_target = p.get('puuid') == puuid
            champ_name = champ_info['name']
            if is_target:
                line = f"⭐ **{champ_name}** — **`{p_riot_id}`** *(Alvo)*"
            else:
                line = f"• **{champ_name}** — `{p_riot_id}`"

            if p.get('teamId') == 100:
                blue_team.append(line)
            else:
                red_team.append(line)

        patch_version = await get_ddragon_version()
        embed = discord.Embed(
            title=f"⚔️ Partida Ao Vivo — {queue_name}",
            description=f"⏱️ **Tempo de jogo:** `{time_str}`\n🎲 **Modo:** `{game_data.get('gameMode', 'SR')}`",
            color=discord.Color.blue()
        )
        embed.set_author(name=f"Partida de {riot_id}", icon_url=ctx.author.display_avatar.url)

        if blue_team:
            embed.add_field(name="🔵 Time Azul", value="\n".join(blue_team), inline=False)
        if red_team:
            embed.add_field(name="🔴 Time Vermelho", value="\n".join(red_team), inline=False)

        # Bans (se houver)
        banned = game_data.get('bannedChampions', [])
        if banned:
            blue_bans = []
            red_bans = []
            for b in banned:
                cid = b.get('championId', -1)
                if cid > 0:
                    cinfo = await get_champion_by_key(cid)
                    if b.get('teamId') == 100:
                        blue_bans.append(cinfo['name'])
                    else:
                        red_bans.append(cinfo['name'])

            bans_text = ""
            if blue_bans:
                bans_text += f"🔵 **Azul:** {', '.join(blue_bans)}\n"
            if red_bans:
                bans_text += f"🔴 **Vermelho:** {', '.join(red_bans)}"
            if bans_text:
                embed.add_field(name="🚫 Campeões Banidos", value=bans_text, inline=False)

        opgg_live = f"https://www.op.gg/summoners/br/{name_encoded}-{tag_encoded}/ingame"
        embed.add_field(name="🔗 Mais Detalhes", value=f"[Ver partida ao vivo no OP.GG]({opgg_live})", inline=False)
        embed.set_footer(text=f"Patch {patch_version} • Solicitado por {ctx.author.display_name}")

        await ctx.send(embed=embed)
