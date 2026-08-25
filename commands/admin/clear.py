import discord
from discord.ext import commands

def setup_clear_command(bot):
    @bot.command(name="clear", aliases=["limpar"])
    @commands.has_permissions(manage_messages=True)
    async def clear(ctx, amount: int = None):
        if amount is None:
            return await ctx.send(f"Uso correto: `{ctx.prefix}clear <quantidade>`", delete_after=5)
        
        if amount < 1 or amount > 100:
            return await ctx.send("Você só pode apagar entre 1 e 100 mensagens por vez.", delete_after=5)

        # Somamos 1 ao limite para apagar também a mensagem que disparou o comando
        deleted = await ctx.channel.purge(limit=amount + 1)
        
        # Enviamos uma confirmação que se auto-deleta em 5 segundos para manter o chat limpo
        await ctx.send(f"✅ Removi {len(deleted) - 1} mensagens.", delete_after=5)

    @clear.error
    async def clear_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você não tem permissão de `Gerenciar Mensagens` para usar este comando.", delete_after=5)