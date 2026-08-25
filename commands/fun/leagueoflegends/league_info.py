import discord
from discord.ext import commands
import aiohttp
from urllib.parse import quote
from commands.fun.leagueoflegends.riot_api_utils import fetch_riot_api

def setup_league_info_command(bot):
    @bot.command(name="leagueinfo", aliases=["lol", "lolstats", "lolprofile", "leagueprofile"])
    async def leagueinfo(ctx, member: discord.Member = None):
        """Mostra informações de LoL de um usuário vinculado"""
        member = member or ctx.author
        data = await bot.db.fetch_one("SELECT riot_id FROM leagueconfig WHERE user_id = %s", (member.id,))
        if not data:
            return await ctx.send(f"❌ {member.display_name} não vinculou uma conta. Use `{ctx.prefix}linkleague Nome#TAG`.")

        riot_id = data['riot_id']
        if "#" not in riot_id:
            return await ctx.send("❌ Erro: O Riot ID salvo no banco está em formato inválido.")
            
        name, tag = riot_id.rsplit("#", 1)
        name_encoded, tag_encoded = quote(name), quote(tag)

        # 1. Pegar PUUID (Account-V1)
        acc_data = await fetch_riot_api(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name_encoded}/{tag_encoded}")
        if not acc_data: 
            return await ctx.send(f"❌ Conta `{riot_id}` não encontrada (Account-V1). Verifique se o nome e a tag estão corretos.")
        puuid = acc_data['puuid']

        # 2. Pegar Elos Diretamente por PUUID (League-V4)
        league_data = await fetch_riot_api(f"https://br1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}")
        
        if league_data is None:
            return await ctx.send(f"❌ Não foi possível encontrar dados de ranking para `{riot_id}` no servidor BR. Verifique se o jogador possui partidas ranqueadas nesta região.")
        
        solo_rank = "Unranked"
        flex_rank = "Unranked"

        for entry in league_data:
            wins = entry['wins']
            losses = entry['losses']
            total = wins + losses
            wr = (wins / total) * 100 if total > 0 else 0
            
            rank_str = f"{entry['tier']} {entry['rank']} ({entry['leaguePoints']} LP)\n{wins}W/{losses}L ({wr:.1f}%)"
            if entry['queueType'] == "RANKED_SOLO_5x5": solo_rank = rank_str
            elif entry['queueType'] == "RANKED_FLEX_SR": flex_rank = rank_str

        # 3. Pegar Maestria (Champion-Mastery-V4)
        mastery_data = await fetch_riot_api(f"https://br1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=1")
        
        champ_name = "Desconhecido"
        champ_img = ""
        
        if mastery_data:
            champ_id = mastery_data[0]['championId']
            async with aiohttp.ClientSession() as session:
                async with session.get("https://ddragon.leagueoflegends.com/cdn/15.1.1/data/pt_BR/champion.json") as r:
                    if r.status == 200:
                        champions_data = await r.json()
                        for c_name, c_info in champions_data['data'].items():
                            if c_info['key'] == str(champ_id):
                                champ_name = c_name
                                champ_img = f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{c_name}_0.jpg"
                                break

        embed = discord.Embed(title=f"📊 {riot_id}", color=discord.Color.blue())
            
        embed.add_field(name="🏆 Solo/Duo", value=solo_rank, inline=True)
        embed.add_field(name="👥 Flex", value=flex_rank, inline=True)
        
        if mastery_data:
            mastery_pts = mastery_data[0]['championPoints']
            embed.add_field(name="🔥 Maior Maestria", value=f"{champ_name} ({mastery_pts:,} pts)", inline=False)
            embed.set_thumbnail(url=champ_img)

        await ctx.send(embed=embed)