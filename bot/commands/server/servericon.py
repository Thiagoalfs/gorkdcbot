import discord, json, os
from commands.languageservice import languageservice

def server_icon(bot):
    @bot.command(name="servericon")
    async def server_icon(ctx):

        guild = ctx.guild
        icon_url = guild.icon.url if guild.icon else None
        if icon_url:
            embed = discord.Embed(title=f"{guild.name}", color=discord.Color.blue())
            embed.set_image(url=icon_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Server ``{guild.name}`` has no icon.")