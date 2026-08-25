from discord.ext import commands

def setup_prefix_command(bot):
    @bot.command(name="prefix", aliases=["prefixo", "setprefix"])
    @commands.has_permissions(administrator=True)
    async def prefix(ctx, new_prefix: str = None):
        if not new_prefix:
            return await ctx.send(f"O prefixo atual é `{ctx.prefix}`. Use `{ctx.prefix}prefix <novo>` para mudar.")

        if len(new_prefix) > 5:
            return await ctx.send("O prefixo é muito longo! Máximo de 5 caracteres.")

        await bot.db.execute("""
            INSERT INTO botsettings (guild_id, serverprefix) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE serverprefix = %s
        """, (ctx.guild.id, new_prefix, new_prefix))

        # Atualiza o cache imediatamente
        bot.prefix_cache[ctx.guild.id] = new_prefix

        await ctx.send(f"✅ Prefixo alterado com sucesso para `{new_prefix}`")

    @prefix.error
    async def prefix_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você precisa da permissão de `Administrador` para alterar o prefixo.", delete_after=5)