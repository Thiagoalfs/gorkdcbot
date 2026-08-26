import discord
from discord.ext import commands

def setup_resume_command(bot):
    @bot.hybrid_command(
        name="resume",
        aliases=["despausar", "continuar", "unpause"],
        description="Retoma a música que estava pausada"
    )
    async def resume(ctx):
        if not ctx.voice_client:
            return await ctx.send("❌ Eu nem tô em canal de voz nenhum, ze.", ephemeral=True)

        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.send("❌ Você precisa estar na mesma call que eu pra despausar!", ephemeral=True)

        if not ctx.voice_client.is_paused():
            if ctx.voice_client.is_playing():
                return await ctx.send("⚠️ A música já está tocando normalmente!", ephemeral=True)
            return await ctx.send("❌ Nenhuma música está pausada para ser retomada.", ephemeral=True)

        ctx.voice_client.resume()
        await ctx.send("▶️ Música retomada!")
