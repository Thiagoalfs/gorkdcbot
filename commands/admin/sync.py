import discord
from discord.ext import commands


def setup_sync_command(bot):
    @bot.command(
        name="sync",
        aliases=["resync", "clearslash"],
        description="Limpa slash commands antigos dos servidores e ressincroniza os atuais",
        hidden=True,
    )
    @commands.is_owner()
    async def sync(ctx):
        msg = await ctx.send("⏳ Limpando slash commands antigos dos servidores e sincronizando os atuais...")

        cleared_guilds = 0
        failed_guilds = 0

        for guild in bot.guilds:
            try:
                bot.tree.clear_commands(guild=guild)
                await bot.tree.sync(guild=guild)
                cleared_guilds += 1
            except Exception as e:
                failed_guilds += 1
                print(f"[SYNC] Falha ao limpar comandos da guild {guild.name} ({guild.id}): {e}")

        synced = await bot.tree.sync()

        summary = (
            f"✅ Sincronização concluída!\n"
            f"• **Servidores limpos:** {cleared_guilds}"
        )
        if failed_guilds:
            summary += f" ({failed_guilds} falharam)"
        summary += (
            f"\n• **Slash Commands globais ativos:** {len(synced)}\n"
            f"💡 *Se ainda aparecer algum comando antigo no seu Discord, aperte `Ctrl + R` para limpar o cache do cliente.*"
        )

        await msg.edit(content=summary)

    @sync.error
    async def sync_error(ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("❌ Apenas o dono do bot pode usar este comando.", delete_after=5)
        else:
            await ctx.send(f"❌ Erro ao sincronizar comandos: {error}")
