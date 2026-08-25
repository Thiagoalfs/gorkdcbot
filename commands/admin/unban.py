import discord
from discord.ext import commands

def setup_unban_command(bot):
    @bot.command(name="unban", aliases=["desbanir"])
    @commands.has_permissions(ban_members=True)
    async def unban(ctx, user_id: int, *, reason: str = None):
        reason = reason or "Nenhuma razão fornecida."

        try:
            user = await bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=reason)
            await ctx.send(f"✅ {user.name} foi desbanido(a) por: {reason}", delete_after=10)
        except discord.NotFound:
            await ctx.send(f"❌ Usuário com ID `{user_id}` não encontrado na lista de banidos.", delete_after=5)
        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro ao tentar desbanir o usuário: {e}", delete_after=5)

    @unban.error
    async def unban_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você não tem permissão de `Banir Membros` para usar este comando.", delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Por favor, forneça o ID do usuário que você deseja desbanir. Ex: `{ctx.prefix}unban <ID_do_usuário> [razão]`", delete_after=5)
