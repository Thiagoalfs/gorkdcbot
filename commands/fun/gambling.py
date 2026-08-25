import random
import discord
import asyncio

def setup_gambling_command(bot):
    @bot.command(name="gambling", aliases=["gamble", "apostar"])
    async def gambling(ctx):
        emojis = ["🎲", "🎰", "🃏", "💰", "💸", "🤑"]
        total_slots = 3

        # Sorteia os emojis da rodada
        results = [random.choice(emojis) for _ in range(total_slots)]
        slots = ["❓"] * total_slots

        # Envia o embed inicial com o primeiro slot revelado
        slots[0] = f"**{results[0]}**"
        embed = discord.Embed(title="🎰 Cassino", color=discord.Color.gold())
        embed.description = " | ".join(slots)
        msg = await ctx.send(embed=embed, reference=ctx.message)

        # Revela os demais slots sequencialmente usando um for loop
        for i in range(1, total_slots):
            await asyncio.sleep(1)
            slots[i] = f"**{results[i]}**"
            embed.description = " | ".join(slots)
            await msg.edit(embed=embed)

        # Verifica se todos os emojis sorteados são iguais
        if len(set(results)) == 1:
            embed.color = discord.Color.green()
            embed.add_field(name="Resultado", value="Parabéns! Você tirou o jackpot! 🎉")
        else:
            embed.color = discord.Color.red()
            embed.add_field(name="Resultado", value="Não foi dessa vez... tente novamente! ❌")

        await msg.edit(embed=embed)
