import os
import shutil
import asyncio
from commands.songs.vcplay import song_queues
from generalFunctions import BASE_DOWNLOAD_FOLDER

def setup_stop_command(bot):
    @bot.command(name="stop", aliases=["parar", "sair", "dc"])
    async def stop(ctx):
        guild_id = ctx.guild.id

        if not ctx.voice_client:
            return await ctx.send("Eu nem tô em call nenhuma, ze.")

        if not ctx.author.voice or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.send("Tu tem que tá na call pra me parar, pnc.")

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        
        await ctx.voice_client.disconnect(force=True)

        if guild_id in song_queues:
            del song_queues[guild_id]

        await asyncio.sleep(0.5)

        guild_folder = os.path.join(BASE_DOWNLOAD_FOLDER, str(guild_id))
        try:
            if os.path.exists(guild_folder):
                shutil.rmtree(guild_folder)
            print(f"[CLEANUP] Pasta de audio do servidor {guild_id} removida com sucesso.")
        except Exception as e:
            print(f"[ERROR] Falha ao limpar pasta do servidor {guild_id}: {e}")

        await ctx.send("Flw!")
