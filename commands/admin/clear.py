import discord
from discord.ext import commands

def setup_clear_command(bot):
    @bot.hybrid_command(name="clear", aliases=["limpar"], description="Apaga um número de mensagens do chat (1 a 100)")
    @commands.has_permissions(manage_messages=True)
    async def clear(ctx, amount: int = 10):
        if amount < 1 or amount > 100:
            return await ctx.send("Você só pode apagar entre 1 e 100 mensagens por vez.", ephemeral=True)

        # Se for comando de prefixo, apagamos a mensagem do comando também
        limit = amount if ctx.interaction else amount + 1
        deleted = await ctx.channel.purge(limit=limit)
        count = len(deleted) if ctx.interaction else max(0, len(deleted) - 1)
        
        await ctx.send(f"✅ Removi **{count}** mensagens.", ephemeral=True)

    @clear.error
    async def clear_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você não tem permissão de `Gerenciar Mensagens` para usar este comando.", ephemeral=True)
