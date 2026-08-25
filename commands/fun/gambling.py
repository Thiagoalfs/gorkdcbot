import random
import discord
import asyncio

def setup_gambling_command(bot):
    @bot.hybrid_command(name="gambling", aliases=["gamble", "apostar"], description="Gira a roleta de emojis do cassino")
    async def gambling(ctx):
        emojis = ["🎲", "🎰", "🃏", "💰", "💸", "🤑"]
        total_slots = 3

        results = [random.choice(emojis) for _ in range(total_slots)]
        slots = ["❓"] * total_slots

        slots[0] = f"**{results[0]}**"
        embed = discord.Embed(title="🎰 Cassino", color=discord.Color.gold())
        embed.description = " | ".join(slots)
        msg = await ctx.send(embed=embed)

        for i in range(1, total_slots):
            await asyncio.sleep(1)
            slots[i] = f"**{results[i]}**"
            embed.description = " | ".join(slots)
            if ctx.interaction:
                await ctx.interaction.edit_original_response(embed=embed)
            else:
                await msg.edit(embed=embed)

        if len(set(results)) == 1:
            embed.color = discord.Color.green()
            embed.add_field(name="Resultado", value="Parabéns! Você tirou o jackpot! 🎉")
        else:
            embed.color = discord.Color.red()
            embed.add_field(name="Resultado", value="Não foi dessa vez... tente novamente! ❌")

        if ctx.interaction:
            await ctx.interaction.edit_original_response(embed=embed)
        else:
            await msg.edit(embed=embed)
