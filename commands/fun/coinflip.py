import random

def coin_flip(bot):
    @bot.command(name="coinflip", aliases=["coin"])
    async def coin_flip(ctx):
        result = random.choice(["cara", "coroa"])
        await ctx.send(result, reference=ctx.message)