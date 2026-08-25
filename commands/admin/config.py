import discord
from discord.ext import commands

def setup_config_command(bot):
    @bot.command(name="config", aliases=["settings", "configurar"])
    @commands.has_permissions(administrator=True)
    async def config(ctx):
        embed = discord.Embed(
            title="⚙️ Painel de Configuração",
            description="Aqui estão os comandos fundamentais para ajustar as preferências do bot neste servidor.",
            color=discord.Color.blue()
        )

        embed.add_field(
            name=f"🔡 Prefixo (`{ctx.prefix}prefix`)",
            value="Altera o caractere usado antes dos comandos.",
            inline=False
        )

        embed.set_footer(text=f"Dica: Use {ctx.prefix}help <comando> para ver detalhes de uso.")
        await ctx.send(embed=embed)
