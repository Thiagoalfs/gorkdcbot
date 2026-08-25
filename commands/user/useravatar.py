import discord

def useravatar(bot):
    @bot.command(name="useravatar", aliases=["avatar"])
    async def avatar(ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        avatar_url = member.display_avatar.url
        embed = discord.Embed(title=f"{member.display_name}", color=discord.Color.blue())
        embed.set_image(url=avatar_url)
        await ctx.send(embed=embed, reference=ctx.message)