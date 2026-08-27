import discord
from discord.ext import commands
import random
import time
from urllib.parse import quote
from commands.fun.leagueoflegends.riot_api_utils import (
    fetch_riot_api, 
    get_champion_by_key, 
    get_ddragon_version, 
    fetch_ddragon_lol_data
)

ROLES = ["Topo", "Selva", "Meio", "Atirador", "Suporte"]
SUMMONERS = ["Flash", "Incendiar", "Teleporte", "Curar", "Barreira", "Exaustão", "Fantasma", "Purificar", "Golpear"]

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

def setup_league_commands(bot):
    @bot.hybrid_group(
        name="league", 
        aliases=["lol"], 
        description="Comandos relacionados a League of Legends"
    )
    async def league_group(ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🎮 Comandos de League of Legends",
                description="Use um dos subcomandos abaixo:",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="📊 Perfil e Estatísticas",
                value=f"`{ctx.prefix}league profile [@membro]` ou `/league profile`\nMostra elo, maestrias, nível e link do OP.GG.",
                inline=False
            )
            embed.add_field(
                name="⚔️ Partida Ao Vivo",
                value=f"`{ctx.prefix}league game [@membro / Nome#TAG]` ou `/league game`\nMostra a partida em andamento, times, bans e tempo de jogo.",
                inline=False
            )
            embed.add_field(
                name="🔗 Vincular Conta",
                value=f"`{ctx.prefix}league link <Nome#TAG>` ou `/league link`\nVincula sua conta Riot ao seu Discord.",
                inline=False
            )
            embed.add_field(
                name="🎲 Desafio de Build",
                value=f"`{ctx.prefix}league gen [campeão]` ou `/league gen`\nGera um campeão, rota, feitiços e itens aleatórios.",
                inline=False
            )
            await ctx.send(embed=embed, ephemeral=True)

    # ----------------------------------------------------
    # 1. Subcomando: PROFILE (/league profile)
    # ----------------------------------------------------
    @league_group.command(
        name="profile", 
        aliases=["info", "perfil", "stats"],
        description="Mostra o perfil completo de League of Legends de um usuário"
    )
    async def profile(ctx, member: discord.Member = None):
        await ctx.defer()
        member = member or ctx.author
        data = await bot.db.fetch_one("SELECT riot_id FROM leagueconfig WHERE user_id = %s", (member.id,))
        if not data:
            return await ctx.send(f"❌ **{member.display_name}** não vinculou uma conta. Use `/league link Nome#TAG`.")

        riot_id = data['riot_id']
        if "#" not in riot_id:
            return await ctx.send("❌ Erro: O Riot ID salvo no banco está em formato inválido.")
            
        name, tag = riot_id.rsplit("#", 1)
        name_encoded, tag_encoded = quote(name), quote(tag)

        acc_data = await fetch_riot_api(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name_encoded}/{tag_encoded}")
        if not acc_data: 
            return await ctx.send(f"❌ Conta `{riot_id}` não encontrada. Verifique se o nome e a tag estão corretos. `/league link (Nome#TAG)`.")
        puuid = acc_data['puuid']

        summoner_data = await fetch_riot_api(f"https://br1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}")
        summoner_level = summoner_data.get('summonerLevel', 0) if summoner_data else 0
        profile_icon_id = summoner_data.get('profileIconId', 1) if summoner_data else 1

        league_data = await fetch_riot_api(f"https://br1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}")
        
        solo_rank = "Unranked"
        flex_rank = "Unranked"

        if league_data:
            for entry in league_data:
                wins = entry['wins']
                losses = entry['losses']
                total = wins + losses
                wr = (wins / total) * 100 if total > 0 else 0
                
                tier = entry['tier'].capitalize()
                rank = entry['rank']
                lp = entry['leaguePoints']
                rank_str = f"**{tier} {rank}** ({lp} LP)\n`{wins}V {losses}D` • **{wr:.1f}% WR**"
                
                if entry['queueType'] == "RANKED_SOLO_5x5":
                    solo_rank = rank_str
                elif entry['queueType'] == "RANKED_FLEX_SR":
                    flex_rank = rank_str

        mastery_data = await fetch_riot_api(f"https://br1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=3")
        
        patch_version = await get_ddragon_version()
        masteries_list = []
        top1_champ_img = ""

        medals = ["🥇", "🥈", "🥉"]

        if mastery_data:
            for index, mastery in enumerate(mastery_data):
                champ_id = mastery['championId']
                champ_pts = mastery['championPoints']
                champ_lvl = mastery.get('championLevel', 1)
                
                champ_info = await get_champion_by_key(champ_id)
                champ_name = champ_info['name']
                
                if index == 0:
                    top1_champ_img = f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champ_info['id']}_0.jpg"

                medal = medals[index] if index < len(medals) else "•"
                masteries_list.append(f"{medal} **{champ_name}** (M{champ_lvl}) — `{champ_pts:,} pts`".replace(",", "."))

        embed = discord.Embed(
            title="📊 Perfil de League of Legends",
            color=discord.Color.blue()
        )

        icon_url = f"https://ddragon.leagueoflegends.com/cdn/{patch_version}/img/profileicon/{profile_icon_id}.png"
        embed.set_author(name=f"{riot_id} (Nível {summoner_level})", icon_url=icon_url)
        
        embed.add_field(name="🏆 Solo/Duo", value=solo_rank, inline=True)
        embed.add_field(name="👥 Flex", value=flex_rank, inline=True)

        if masteries_list:
            embed.add_field(
                name="🔥 Top 3 Campeões Mais Jogados", 
                value="\n".join(masteries_list), 
                inline=False
            )

        if top1_champ_img:
            embed.set_thumbnail(url=top1_champ_img)

        opgg_url = f"https://www.op.gg/summoners/br/{quote(name)}-{quote(tag)}"
        embed.add_field(
            name="🔗 Links Úteis", 
            value=f"[Ver estatísticas no OP.GG]({opgg_url})", 
            inline=False
        )

        embed.set_footer(
            text=f"Patch {patch_version} • Solicitado por {ctx.author.display_name}", 
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)

    # ----------------------------------------------------
    # 2. Subcomando: GAME (/league game)
    # ----------------------------------------------------
    @league_group.command(
        name="game",
        aliases=["partida", "live", "ingame"],
        description="Mostra informações da partida ao vivo de um jogador de LoL"
    )
    async def game(ctx, *, usuario: str = None):
        await ctx.defer()

        riot_id = None
        target_member = None

        if ctx.message and ctx.message.mentions:
            target_member = ctx.message.mentions[0]
        elif usuario:
            clean_str = usuario.strip("<@!> ")
            if clean_str.isdigit():
                target_member = ctx.guild.get_member(int(clean_str)) if ctx.guild else None
            elif "#" in usuario:
                riot_id = usuario.strip()

        if not riot_id:
            target_member = target_member or ctx.author
            data = await bot.db.fetch_one("SELECT riot_id FROM leagueconfig WHERE user_id = %s", (target_member.id,))
            if not data:
                if target_member == ctx.author:
                    return await ctx.send("❌ Você não vinculou uma conta. Use `/league link Nome#TAG` ou informe: `/league game Nome#TAG`.")
                else:
                    return await ctx.send(f"❌ **{target_member.display_name}** não vinculou uma conta no bot.")
            riot_id = data['riot_id']

        if "#" not in riot_id:
            return await ctx.send("❌ Formato de Riot ID inválido. Use `Nome#TAG`.")

        name, tag = riot_id.rsplit("#", 1)
        name_encoded, tag_encoded = quote(name), quote(tag)

        acc_data = await fetch_riot_api(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name_encoded}/{tag_encoded}")
        if not acc_data:
            return await ctx.send(f"❌ Conta `{riot_id}` não encontrada na Riot Games.")
        puuid = acc_data['puuid']

        game_data = await fetch_riot_api(f"https://br1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}")
        if not game_data:
            return await ctx.send(f"❌ **{riot_id}** não está em nenhuma partida ativa no momento.")

        queue_id = game_data.get('gameQueueConfigId', 0)
        queue_name = QUEUE_TYPES.get(queue_id, game_data.get('gameMode', 'Personalizada'))

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

    # ----------------------------------------------------
    # 3. Subcomando: LINK (/league link)
    # ----------------------------------------------------
    @league_group.command(
        name="link", 
        aliases=["vincular"],
        description="Vincula sua conta Riot (Nome#TAG) ao seu usuário do Discord"
    )
    async def link(ctx, *, riot_id: str = None):
        if riot_id is None:
            data = await bot.db.fetch_one("SELECT riot_id FROM leagueconfig WHERE user_id = %s", (ctx.author.id,))
            if data:
                return await ctx.send(f"✅ Sua conta do LoL vinculada atualmente é: `{data['riot_id']}`")
            else:
                return await ctx.send(f"❌ Você não tem uma conta vinculada. Use `{ctx.prefix}league link Nome#TAG`.")

        if "#" not in riot_id:
            return await ctx.send("❌ Use o formato correto: `Nome#TAG` (ex: Grok#BR1)", ephemeral=True)

        await bot.db.execute("""
            INSERT INTO leagueconfig (user_id, riot_id) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE riot_id = %s
        """, (ctx.author.id, riot_id, riot_id))

        await ctx.send(f"✅ Conta `{riot_id}` vinculada com sucesso!")

    # ----------------------------------------------------
    # 4. Subcomando: GEN / BUILD (/league gen)
    # ----------------------------------------------------
    @league_group.command(
        name="gen", 
        aliases=["build", "gerar"],
        description="Gera um desafio aleatório de campeão, rota, feitiços e itens do LoL"
    )
    async def gen(ctx, *, campeao: str = None):
        await ctx.defer()
        lol_data = await fetch_ddragon_lol_data()
        if not lol_data:
            return await ctx.send("❌ Erro ao conectar com o Data Dragon da Riot Games.")

        champions = lol_data["champions"]
        boots = lol_data["boots"]
        items = lol_data["items"]
        
        if campeao:
            champion_obj = next(
                (c for c in champions if c["name"].lower() == campeao.lower() or c["id"].lower() == campeao.lower()), 
                None
            )
            if not champion_obj:
                return await ctx.send(f"❌ Não encontrei o campeão `{campeao}` na lista oficial da Riot Games.")
        else:
            champion_obj = random.choice(champions)
        
        champion_name = champion_obj["name"]
        champ_img_id = champion_obj["id"]
        
        selected_role = random.choice(ROLES)
        
        if selected_role == "Selva":
            other_spells = [s for s in SUMMONERS if s != "Golpear"]
            selected_summoners = ["Golpear", random.choice(other_spells)]
            random.shuffle(selected_summoners)
        else:
            non_smite_spells = [s for s in SUMMONERS if s != "Golpear"]
            selected_summoners = random.sample(non_smite_spells, 2)
        
        if selected_role == "Atirador":
            selected_items = random.sample(items, 6)
        elif selected_role == "Suporte":
            selected_items = ["Item de Suporte"] + random.sample(items, 4)
        else:
            selected_items = random.sample(items, 5)

        chosen_boot = random.choice(boots)

        embed = discord.Embed(title="🎮 Desafio de Build", color=discord.Color.blue())
        embed.set_thumbnail(url=f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champ_img_id}_0.jpg")
        
        embed.add_field(name="👤 Campeão", value=champion_name, inline=True)
        embed.add_field(name="🗺️ Rota", value=selected_role, inline=True)
        embed.add_field(name="⚡ Feitiços", value=" & ".join(selected_summoners), inline=False)
        embed.add_field(name="🥾 Bota", value=f"• {chosen_boot}", inline=False)
        embed.add_field(name="⚔️ Itens", value="\n".join([f"• {i}" for i in selected_items]), inline=False)
        
        embed.set_footer(text=f"Patch {lol_data.get('version', '')} • Boa sorte no Rift, {ctx.author.display_name}!")
        await ctx.send(embed=embed)
