import discord
from discord.ext import commands

def userinfo(bot):
    @bot.command(name="userinfo", aliases=["user"])
    async def userinfo(ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        embed = discord.Embed(title=member.display_name, color=discord.Color.blue())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_author(name=f"Informações de {member.name}")
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Criada em", value=f"{discord.utils.format_dt(member.created_at, style='f')} ({discord.utils.format_dt(member.created_at, style='R')})", inline=False)
        embed.add_field(name="Entrou em", value=f"{discord.utils.format_dt(member.joined_at, style='f')} ({discord.utils.format_dt(member.joined_at, style='R')})" if member.joined_at else "N/A", inline=False)
        await ctx.send(embed=embed, reference=ctx.message)

    @userinfo.error
    async def user_info_error(ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send(f"❌ Usuário não encontrado. Use `{ctx.prefix}userinfo <@membro>` ou o ID.")
        else:
            print(f"Erro no comando userinfo: {error}")
