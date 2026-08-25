import discord
import random
from commands.fun.leagueoflegends.riot_api_utils import fetch_ddragon_lol_data

ROLES = ["Topo", "Selva", "Meio", "Atirador", "Suporte"]
SUMMONERS = ["Flash", "Incendiar", "Teleporte", "Curar", "Barreira", "Exaustão", "Fantasma", "Purificar", "Golpear"]

def setup_lolgen_command(bot):
    @bot.hybrid_command(
        name="lolgen", 
        description="Gera um desafio aleatório de campeão, rota, feitiços e itens do LoL"
    )
    async def lolgen(ctx, *, campeao: str = None):
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
