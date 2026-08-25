import discord
from discord.ext import commands

def setup_kick_command(bot):
    @bot.command(name="kick", aliases=["expulsar"])
    @commands.has_permissions(kick_members=True)
    async def kick(ctx, member: discord.Member, *, reason: str = None):
        reason = reason or "Nenhuma razão fornecida."

        if member == ctx.author:
            return await ctx.send("❌ Você não pode expulsar a si mesmo!", delete_after=5)
        if member == bot.user:
            return await ctx.send("❌ Eu não posso me expulsar!", delete_after=5)
        if ctx.author.top_role <= member.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ Você não pode expulsar um membro com cargo igual ou superior ao seu.", delete_after=5)

        await member.kick(reason=reason)
        await ctx.send(f"✅ {member.display_name} foi expulso(a) por: {reason}", delete_after=10)

    @kick.error
    async def kick_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você não tem permissão de `Expulsar Membros` para usar este comando.", delete_after=5)
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Membro não encontrado. Use `{ctx.prefix}kick <@membro> [razão]`.", delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Por favor, mencione o membro que você deseja expulsar. Ex: `{ctx.prefix}kick @membro [razão]`", delete_after=5)