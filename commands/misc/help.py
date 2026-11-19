import discord
from discord.ext import commands

CATEGORY_MAP = [
    ("commands.fun.leagueoflegends", ("⚔️", "LOL")),
    ("commands.songs", ("🎶", "Músicas")),
    ("commands.user", ("👤", "Usuário")),
    ("commands.fun", ("🎲", "Diversão")),
    ("commands.server", ("🪄", "Server")),
    ("commands.admin", ("⚙️", "Admin")),
    ("commands.misc", ("📌", "Miscelâneas")),
]
DEFAULT_CATEGORY = ("📌", "Outros")


def get_category(cmd: commands.Command):
    root = cmd.root_parent or cmd
    mod = getattr(root.callback, "__module__", "")
    for prefix, category in CATEGORY_MAP:
        if mod.startswith(prefix):
            return category
    return DEFAULT_CATEGORY


def get_description(cmd: commands.Command) -> str:
    return cmd.description or cmd.help or "Sem descrição disponível."


def format_signature(prefix: str, cmd: commands.Command) -> str:
    custom_syntax = cmd.extras.get("sintaxe")
    if custom_syntax:
        return f"{prefix}{custom_syntax}"

    if isinstance(cmd, commands.Group) and cmd.commands and not cmd.signature:
        sub_names = "|".join(sorted(sub.name for sub in cmd.commands if not sub.hidden))
        return f"{prefix}{cmd.qualified_name} <{sub_names}>"

    if cmd.signature:
        return f"{prefix}{cmd.qualified_name} {cmd.signature}"

    return f"{prefix}{cmd.qualified_name}"


def setup_help_command(bot):
    @bot.hybrid_command(
        name="help",
        aliases=["ajuda"],
        description="Mostra a lista de comandos ou detalhes de um comando",
    )
    async def help_command(ctx, *, comando: str = None):
        if not comando:
            embed = discord.Embed(title="🔎 Lista de Comandos", color=discord.Color.blue())
            if ctx.guild and ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon.url)

            is_admin = (
                getattr(ctx.author.guild_permissions, "administrator", False)
                if ctx.guild
                else False
            )

            categories = {}
            for cmd in bot.commands:
                if cmd.hidden:
                    continue
                icon, cat_name = get_category(cmd)
                if cat_name.lower() == "admin" and not is_admin:
                    continue
                if cat_name not in categories:
                    categories[cat_name] = {"icon": icon, "commands": []}
                categories[cat_name]["commands"].append(cmd.name)

            ordered_names = [cat_name for _, (_, cat_name) in CATEGORY_MAP]
            for cat_name in sorted(
                categories.keys(),
                key=lambda name: (
                    ordered_names.index(name) if name in ordered_names else len(ordered_names),
                    name,
                ),
            ):
                cat_data = categories[cat_name]
                field_name = f"{cat_data['icon']} {cat_name}"
                field_value = "\n".join(sorted(cat_data["commands"]))
                embed.add_field(name=field_name, value=field_value, inline=True)

            embed.set_footer(text=f"Use {ctx.prefix}help <comando> ou /help <comando> para detalhes")
            return await ctx.send(embed=embed)

        found_cmd = bot.get_command(comando.strip().lower())
        if not found_cmd or found_cmd.hidden:
            return await ctx.send(
                f"❌ Comando `{comando}` não encontrado. Use `/help` para ver a lista.",
                ephemeral=True,
            )

        icon, cat_name = get_category(found_cmd)
        embed = discord.Embed(
            title=f"Comando {found_cmd.qualified_name}",
            color=discord.Color.blue(),
        )
        if ctx.guild and ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.set_author(name=f"{icon} {cat_name}")

        formatted_aliases = (
            ", ".join(f"{ctx.prefix}{a}" for a in found_cmd.aliases)
            if found_cmd.aliases
            else "Nenhum"
        )

        embed.add_field(name="📃 Descrição", value=get_description(found_cmd), inline=False)
        embed.add_field(name="🔗 Aliases", value=formatted_aliases, inline=True)
        embed.add_field(
            name="🔎 Sintaxe",
            value=f"`{format_signature(ctx.prefix, found_cmd)}`",
            inline=True,
        )

        if isinstance(found_cmd, commands.Group) and found_cmd.commands:
            sub_lines = [
                f"• `{sub.name}` — {get_description(sub)}"
                for sub in sorted(found_cmd.commands, key=lambda c: c.name)
                if not sub.hidden
            ]
            if sub_lines:
                embed.add_field(
                    name="📂 Subcomandos",
                    value="\n".join(sub_lines),
                    inline=False,
                )

        await ctx.send(embed=embed)
