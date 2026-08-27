import discord

HELP_DATABASE = {
    "play": {
        "icon": "🎶", "categoria": "Músicas", "nome": "Comando play",
        "aliases": ["p"],
        "descricao": "Começa a tocar música na call. Aceita links e nomes de músicas. É possível enviar mais de uma música dividindo por vírgulas.",
        "sintaxe": "play <link/nome>"
    },
    "skip": {
        "icon": "🎶", "categoria": "Músicas", "nome": "Comando skip",
        "aliases": ["s", "pular"],
        "descricao": "Pula a música atual.",
        "sintaxe": "skip"
    },
    "stop": {
        "icon": "🎶", "categoria": "Músicas", "nome": "Comando stop",
        "aliases": ["parar", "sair", "dc"],
        "descricao": "Para de tocar músicas e sai da call.",
        "sintaxe": "stop"
    },
    "nowplaying": {
        "icon": "🎶", "categoria": "Músicas", "nome": "Comando nowplaying",
        "aliases": ["np", "tocando"],
        "descricao": "Mostra a música que está tocando agora.",
        "sintaxe": "nowplaying"
    },
    "queue": {
        "icon": "🎶", "categoria": "Músicas", "nome": "Comando queue",
        "aliases": ["q", "fila"],
        "descricao": "Mostra a fila de músicas do servidor.",
        "sintaxe": "queue"
    },
    "download": {
        "icon": "🎶", "categoria": "Músicas", "nome": "Comando download",
        "aliases": ["baixe", "baixar", "instale"],
        "descricao": "Baixa músicas ou vídeos. Caso o arquivo seja maior que 8MB, envia o link do Catbox.",
        "sintaxe": "download <mp3/mp4> <link/nome>"
    },
    "avatar": {
        "icon": "👤", "categoria": "Usuário", "nome": "Comando avatar",
        "aliases": ["useravatar"],
        "descricao": "Mostra o avatar do usuário mencionado ou o seu próprio.",
        "sintaxe": "avatar [@membro]"
    },
    "userinfo": {
        "icon": "👤", "categoria": "Usuário", "nome": "Comando userinfo",
        "aliases": ["user"],
        "descricao": "Mostra informações de cadastro e entrada do usuário no servidor.",
        "sintaxe": "userinfo [@membro]"
    },
    "ping": {
        "icon": "📌", "categoria": "Miscelâneas", "nome": "Comando ping",
        "aliases": [],
        "descricao": "Mostra a latência do bot.",
        "sintaxe": "ping"
    },
    "coinflip": {
        "icon": "🎲", "categoria": "Diversão", "nome": "Comando coinflip",
        "aliases": ["coin"],
        "descricao": "Joga cara ou coroa.",
        "sintaxe": "coinflip"
    },
    "gambling": {
        "icon": "🎲", "categoria": "Diversão", "nome": "Comando gambling",
        "aliases": ["gamble", "apostar"],
        "descricao": "Gira a roleta de emojis do cassino.",
        "sintaxe": "gambling"
    },
    "giveaway": {
        "icon": "🎉", "categoria": "Miscelâneas", "nome": "Comando giveaway",
        "aliases": ["sorteio"],
        "descricao": "Inicia um sorteio no canal indicado com tempo personalizável (segundos, minutos, horas, dias, meses) e contagem de participantes em tempo real via reação.",
        "sintaxe": "giveaway <#canal> <título> <descrição> <tempo> <medida>"
    },
    "league": {
        "icon": "⚔️", "categoria": "LOL", "nome": "Comando league",
        "aliases": ["lol"],
        "descricao": "Comandos de League of Legends. Subcomandos: info (ver perfil e elo), link (vincular conta Riot), gen (desafio de build aleatória).",
        "sintaxe": "league <info|link|gen>"
    },
    "servericon": {
        "icon": "🪄", "categoria": "Server", "nome": "Comando servericon",
        "aliases": [],
        "descricao": "Mostra o ícone atual do servidor.",
        "sintaxe": "servericon"
    },
    "serverinfo": {
        "icon": "🪄", "categoria": "Server", "nome": "Comando serverinfo",
        "aliases": ["si"],
        "descricao": "Mostra informações gerais e estatísticas do servidor.",
        "sintaxe": "serverinfo"
    },
    "prefix": {
        "icon": "⚙️", "categoria": "Admin", "nome": "Comando prefix",
        "aliases": ["prefixo", "setprefix"],
        "descricao": "Altera o prefixo de comandos para este servidor.",
        "sintaxe": "prefix <novo_prefixo>"
    },
    "config": {
        "icon": "⚙️", "categoria": "Admin", "nome": "Comando config",
        "aliases": ["settings", "configurar"],
        "descricao": "Mostra o painel de configurações do servidor.",
        "sintaxe": "config"
    },
    "clear": {
        "icon": "⚙️", "categoria": "Admin", "nome": "Comando clear",
        "aliases": ["limpar"],
        "descricao": "Apaga um número específico de mensagens no chat (entre 1 e 100).",
        "sintaxe": "clear <quantidade>"
    },
    "ban": {
        "icon": "⚙️", "categoria": "Admin", "nome": "Comando ban",
        "aliases": ["banir"],
        "descricao": "Bane um membro do servidor.",
        "sintaxe": "ban <@membro> [razão]"
    },
    "kick": {
        "icon": "⚙️", "categoria": "Admin", "nome": "Comando kick",
        "aliases": ["expulsar"],
        "descricao": "Expulsa um membro do servidor.",
        "sintaxe": "kick <@membro> [razão]"
    },
    "unban": {
        "icon": "⚙️", "categoria": "Admin", "nome": "Comando unban",
        "aliases": ["desbanir"],
        "descricao": "Desbane um usuário pelo ID.",
        "sintaxe": "unban <ID_do_usuário> [razão]"
    }
}

def setup_help_command(bot):
    @bot.hybrid_command(name="help", aliases=["ajuda"], description="Mostra a lista de comandos ou detalhes de um comando")
    async def help_command(ctx, *, comando: str = None):
        if not comando:
            embed = discord.Embed(title="🔎 Lista de Comandos", color=discord.Color.blue())
            if ctx.guild and ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon.url)

            # Agrupa os comandos por categoria a partir do HELP_DATABASE
            categories = {}
            for cmd_name, data in HELP_DATABASE.items():
                cat = data.get("categoria", "Outros")
                icon = data.get("icon", "📌")
                if cat not in categories:
                    categories[cat] = {"icon": icon, "commands": []}
                categories[cat]["commands"].append(cmd_name)

            is_admin = getattr(ctx.author.guild_permissions, "administrator", False) if ctx.guild else False

            for cat_name, cat_data in categories.items():
                if cat_name.lower() == "admin" and not is_admin:
                    continue

                field_name = f"{cat_data['icon']} {cat_name}"
                field_value = "\n".join(cat_data["commands"])
                embed.add_field(name=field_name, value=field_value, inline=True)

            embed.set_footer(text=f"Use {ctx.prefix}help <comando> ou /help <comando> para detalhes")
            return await ctx.send(embed=embed)

        cmd_key = comando.lower()
        found_info = HELP_DATABASE.get(cmd_key)
        if not found_info:
            for key, val in HELP_DATABASE.items():
                if cmd_key in val.get("aliases", []):
                    found_info = val
                    break
        
        if found_info:
            embed = discord.Embed(title=found_info["nome"], color=discord.Color.blue())
            if ctx.guild and ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon.url)
            embed.set_author(name=f"{found_info['icon']} {found_info['categoria']}")
            
            aliases_list = found_info.get("aliases", [])
            formatted_aliases = ", ".join([f"{ctx.prefix}{a}" for a in aliases_list]) if aliases_list else "Nenhum"
            
            embed.add_field(name="📃 Descrição", value=found_info["descricao"], inline=False)
            embed.add_field(name="🔗 Aliases", value=formatted_aliases, inline=True)
            embed.add_field(name="🔎 Sintaxe", value=f"`{ctx.prefix}{found_info['sintaxe']}`", inline=True)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Comando `{comando}` não encontrado. Use `/help` para ver a lista.", ephemeral=True)
