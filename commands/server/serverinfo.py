import discord

def server_info(bot):
    @bot.hybrid_command(name="serverinfo", aliases=["si"], description="Mostra informações detalhadas sobre o servidor")
    async def server_info(ctx):
        guild = ctx.guild
        
        embed = discord.Embed(title=f"{guild.name}", color=discord.Color.blue())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="👑 Dono", value=f"{guild.owner}\n({guild.owner_id})", inline=True)
        embed.add_field(name="🆔 ID do Servidor", value=guild.id, inline=True)
        embed.add_field(name="👥 Membros", value=guild.member_count, inline=True)
        embed.add_field(name="🚀 Impulsos", value=guild.premium_subscription_count, inline=True)
        embed.add_field(name="📅 Criado em", value=f"{discord.utils.format_dt(guild.created_at, style='f')} ({discord.utils.format_dt(guild.created_at, style='R')})", inline=False)
        
        await ctx.send(embed=embed)
