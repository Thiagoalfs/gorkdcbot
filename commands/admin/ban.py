import discord
from discord.ext import commands

def setup_ban_command(bot):
    @bot.hybrid_command(name="ban", aliases=["banir"], description="Bane um membro do servidor")
    @commands.has_permissions(ban_members=True)
    async def ban(ctx, member: discord.Member, *, reason: str = "Nenhuma razão fornecida."):
        if member == ctx.author:
            return await ctx.send("❌ Você não pode banir a si mesmo!", ephemeral=True)
        if member == bot.user:
            return await ctx.send("❌ Eu não posso me banir!", ephemeral=True)
        if ctx.author.top_role <= member.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ Você não pode banir um membro com cargo igual ou superior ao seu.", ephemeral=True)

        await member.ban(reason=reason)
        await ctx.send(f"✅ **{member.display_name}** foi banido(a) por: *{reason}*")

    @ban.error
    async def ban_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você não tem permissão de `Banir Membros` para usar este comando.", ephemeral=True)
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MemberNotFound):
            await ctx.send(f"❌ Membro não encontrado. Use `{ctx.prefix}ban <@membro> [razão]`.", ephemeral=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Por favor, mencione o membro que você deseja banir. Ex: `{ctx.prefix}ban @membro [razão]`", ephemeral=True)
