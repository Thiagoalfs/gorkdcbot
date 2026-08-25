def ping(bot):
    @bot.hybrid_command(name="ping", description="Mostra a latência do bot")
    async def ping(ctx):
        await ctx.send(f"🏓 Pong! Latência: **{round(bot.latency * 1000)}ms**")
