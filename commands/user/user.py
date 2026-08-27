import discord
from discord.ext import commands

def setup_user_commands(bot):
    @bot.hybrid_group(
        name="user",
        aliases=["usuario", "membro"],
        description="Comandos relacionados a usuários e perfil"
    )
    async def user_group(ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="👤 Comandos de Usuário",
                description="Use um dos subcomandos abaixo:",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="🖼️ Avatar do Usuário",
                value=f"`{ctx.prefix}user avatar [@membro]` ou `/user avatar`\nMostra o avatar e imagem de perfil do usuário.",
                inline=False
            )
            embed.add_field(
                name="ℹ️ Informações de Perfil",
                value=f"`{ctx.prefix}user info [@membro]` ou `/user info`\nMostra informações completas da conta, datas e cargos.",
                inline=False
            )
            await ctx.send(embed=embed, ephemeral=True)

    # ----------------------------------------------------
    # 1. Subcomando: AVATAR (/user avatar)
    # ----------------------------------------------------
    @user_group.command(
        name="avatar",
        aliases=["pfp", "icon", "foto"],
        description="Mostra o avatar de um membro ou o seu próprio em alta resolução"
    )
    async def avatar(ctx, member: discord.Member = None):
        await ctx.defer()
        member = member or ctx.author

        try:
            full_user = await bot.fetch_user(member.id)
        except Exception:
            full_user = member

        avatar_url = member.display_avatar.with_size(1024).url
        banner_url = full_user.banner.with_size(1024).url if getattr(full_user, "banner", None) else None

        embed = discord.Embed(
            title=f"🖼️ Avatar de {member.display_name}",
            color=member.color if member.color.value != 0 else discord.Color.blue()
        )
        embed.set_image(url=avatar_url)

        links = [f"[Abrir Avatar em HD]({avatar_url})"]
        if banner_url:
            links.append(f"[Abrir Banner]({banner_url})")

        embed.add_field(name="🔗 Mídia", value=" • ".join(links), inline=False)
        embed.set_footer(
            text=f"Solicitado por {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)

    # ----------------------------------------------------
    # 2. Subcomando: INFO (/user info)
    # ----------------------------------------------------
    @user_group.command(
        name="info",
        aliases=["perfil", "profile", "dados"],
        description="Mostra informações detalhadas sobre um usuário"
    )
    async def info(ctx, member: discord.Member = None):
        await ctx.defer()
        member = member or ctx.author

        try:
            full_user = await bot.fetch_user(member.id)
        except Exception:
            full_user = member

        avatar_url = member.display_avatar.with_size(1024).url
        banner_url = full_user.banner.with_size(1024).url if getattr(full_user, "banner", None) else None

        # Busca dados do League of Legends salvos no banco
        riot_data = None
        try:
            riot_data = await bot.db.fetch_one("SELECT riot_id FROM leagueconfig WHERE user_id = %s", (member.id,))
        except Exception:
            pass

        # Formata os cargos (ocultando @everyone)
        roles = [role.mention for role in reversed(member.roles) if role.name != "@everyone"]
        if len(roles) > 8:
            roles_display = ", ".join(roles[:8]) + f" e mais {len(roles) - 8}..."
        elif roles:
            roles_display = ", ".join(roles)
        else:
            roles_display = "Nenhum cargo especial"

        embed = discord.Embed(
            title=f"👤 Perfil de {member.display_name}",
            description=f"{member.mention} (`{member.name}`)",
            color=member.color if member.color.value != 0 else discord.Color.blue()
        )
        embed.set_thumbnail(url=avatar_url)

        embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
        embed.add_field(
            name="🤖 Tipo", 
            value="Bot" if member.bot else "Usuário", 
            inline=True
        )
        embed.add_field(
            name="👑 Cargo Mais Alto",
            value=member.top_role.mention if member.top_role.name != "@everyone" else "Nenhum",
            inline=True
        )

        embed.add_field(
            name="📅 Conta Criada",
            value=f"<t:{int(member.created_at.timestamp())}:F>\n(<t:{int(member.created_at.timestamp())}:R>)",
            inline=True
        )
        embed.add_field(
            name="📥 Entrou no Servidor",
            value=f"<t:{int(member.joined_at.timestamp())}:F>\n(<t:{int(member.joined_at.timestamp())}:R>)" if member.joined_at else "N/A",
            inline=True
        )

        if riot_data and riot_data.get('riot_id'):
            embed.add_field(
                name="⚔️ Riot ID (LoL)",
                value=f"`{riot_data['riot_id']}` (Use `/league profile` para ver elo)",
                inline=False
            )

        embed.add_field(name=f"🏷️ Cargos ({len(roles)})", value=roles_display, inline=False)

        links = [f"[Avatar HD]({avatar_url})"]
        if banner_url:
            links.append(f"[Banner HD]({banner_url})")
            embed.set_image(url=banner_url)

        embed.add_field(name="🔗 Mídia", value=" • ".join(links), inline=False)
        embed.set_footer(
            text=f"Solicitado por {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)

    @user_group.error
    async def user_error(ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Usuário não encontrado no servidor.", ephemeral=True)
