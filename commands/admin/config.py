import discord
from discord.ext import commands

def setup_config_command(bot):
    @bot.hybrid_command(name="config", aliases=["settings", "configurar"], description="Exibe o painel de configurações do servidor")
    @commands.has_permissions(administrator=True)
    async def config(ctx):
        embed = discord.Embed(
            title="⚙️ Painel de Configuração",
            description="Aqui estão as configurações principais do bot para este servidor.",
            color=discord.Color.blue()
        )

        embed.add_field(
            name=f"🔡 Prefixo (`{ctx.prefix}prefix` ou `/prefix`)",
            value=f"Prefixo atual: `{ctx.prefix}`",
            inline=False
        )

        embed.set_footer(text=f"Dica: Use {ctx.prefix}help <comando> ou /help para ver detalhes de uso.")
        await ctx.send(embed=embed)
