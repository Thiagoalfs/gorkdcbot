import discord

def useravatar(bot):
    @bot.hybrid_command(name="useravatar", aliases=["avatar"], description="Mostra o avatar de um membro ou o seu próprio")
    async def avatar(ctx, member: discord.Member = None):
        member = member or ctx.author
        avatar_url = member.display_avatar.url
        embed = discord.Embed(title=f"Avatar de {member.display_name}", color=discord.Color.blue())
        embed.set_image(url=avatar_url)
        await ctx.send(embed=embed)
