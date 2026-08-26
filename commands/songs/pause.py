import discord
from discord.ext import commands

def setup_pause_command(bot):
    @bot.hybrid_command(
        name="pause",
        aliases=["pausar"],
        description="Pausa a música que está tocando no momento"
    )
    async def pause(ctx):
        if not ctx.voice_client:
            return await ctx.send("❌ Eu nem tô em canal de voz nenhum, ze.", ephemeral=True)

        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.send("❌ Você precisa estar na mesma call que eu pra pausar!", ephemeral=True)

        if ctx.voice_client.is_paused():
            return await ctx.send("⚠️ A música já está pausada! Use `/resume` para continuar.", ephemeral=True)

        if not ctx.voice_client.is_playing():
            return await ctx.send("❌ Não tem nenhuma música tocando no momento.", ephemeral=True)

        ctx.voice_client.pause()
        await ctx.send("⏸️ Música pausada com sucesso! Use `/resume` para continuar.")
