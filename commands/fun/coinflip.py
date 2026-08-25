import random

def coin_flip(bot):
    @bot.hybrid_command(name="coinflip", aliases=["coin"], description="Joga cara ou coroa")
    async def coin_flip(ctx):
        result = random.choice(["🪙 Caiu **Cara**!", "🪙 Caiu **Coroa**!"])
        await ctx.send(result)
