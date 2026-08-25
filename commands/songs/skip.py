from commands.songs.vcplay import song_queues

def setup_skip_command(bot):
    @bot.hybrid_command(name="skip", aliases=["s", "pular"], description="Pula a música que está tocando")
    async def skip(ctx):
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            return await ctx.send("Não tem nada tocando pra eu pular, ze.", ephemeral=True)

        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.send("Entra na call pra pular a música.", ephemeral=True)

        ctx.voice_client.stop()
        await ctx.send("⏭️ Skippando...")
