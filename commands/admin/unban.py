import discord
from discord.ext import commands

def setup_unban_command(bot):
    @bot.hybrid_command(name="unban", aliases=["desbanir"], description="Desbane um usuário pelo ID")
    @commands.has_permissions(ban_members=True)
    async def unban(ctx, user_id: str, *, reason: str = "Nenhuma razão fornecida."):
        try:
            user_id_int = int(user_id)
            user = await bot.fetch_user(user_id_int)
            await ctx.guild.unban(user, reason=reason)
            await ctx.send(f"✅ **{user.name}** foi desbanido(a) por: *{reason}*")
        except ValueError:
            await ctx.send("❌ O ID do usuário deve ser composto apenas por números.", ephemeral=True)
        except discord.NotFound:
            await ctx.send(f"❌ Usuário com ID `{user_id}` não encontrado na lista de banidos.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro ao tentar desbanir o usuário: {e}", ephemeral=True)

    @unban.error
    async def unban_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você não tem permissão de `Banir Membros` para usar este comando.", ephemeral=True)
