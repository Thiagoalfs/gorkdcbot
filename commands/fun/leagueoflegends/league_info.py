import discord
from discord.ext import commands
from urllib.parse import quote
from commands.fun.leagueoflegends.riot_api_utils import fetch_riot_api, get_champion_by_key, get_ddragon_version

def setup_league_info_command(bot):
    @bot.hybrid_command(
        name="leagueinfo", 
        aliases=["lol", "lolstats", "lolprofile", "leagueprofile"],
        description="Mostra o perfil completo de League of Legends de um usuário"
    )
    async def leagueinfo(ctx, member: discord.Member = None):
        await ctx.defer()
        member = member or ctx.author
        data = await bot.db.fetch_one("SELECT riot_id FROM leagueconfig WHERE user_id = %s", (member.id,))
        if not data:
            return await ctx.send(f"❌ **{member.display_name}** não vinculou uma conta. Use `/leaguelink Nome#TAG`.")

        riot_id = data['riot_id']
        if "#" not in riot_id:
            return await ctx.send("❌ Erro: O Riot ID salvo no banco está em formato inválido.")
            
        name, tag = riot_id.rsplit("#", 1)
        name_encoded, tag_encoded = quote(name), quote(tag)

        # 1. Busca os dados de conta (PUUID)
        acc_data = await fetch_riot_api(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name_encoded}/{tag_encoded}")
        if not acc_data: 
            return await ctx.send(f"❌ Conta `{riot_id}` não encontrada. Verifique se o nome e a tag estão corretos.")
        puuid = acc_data['puuid']

        # 2. Busca dados de Invocador (Nível e Ícone de Perfil)
        summoner_data = await fetch_riot_api(f"https://br1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}")
        summoner_level = summoner_data.get('summonerLevel', 0) if summoner_data else 0
        profile_icon_id = summoner_data.get('profileIconId', 1) if summoner_data else 1

        # 3. Busca dados de Ranqueada (Solo/Duo e Flex)
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

        # 4. Busca o Top 3 Campeões com Maior Maestria
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

        # 5. Monta o Embed Completo
        embed = discord.Embed(
            title=f"📊 Perfil de League of Legends",
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
