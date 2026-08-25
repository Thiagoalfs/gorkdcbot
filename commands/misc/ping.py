def ping(bot):
    @bot.command(name="ping")
    async def ping(ctx):
        await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")