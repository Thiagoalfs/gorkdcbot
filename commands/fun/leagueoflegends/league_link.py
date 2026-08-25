from discord.ext import commands

def setup_league_link_command(bot):
    @bot.command(name="leaguelink", aliases=["vincularlol", "linkleague", "lollink", "linklol"])
    async def linkleague(ctx, *, riot_id: str = None):
        """Vincula sua conta do LoL ao Discord (Formato: Nome#Tag)"""
        if riot_id is None:
            data = await bot.db.fetch_one("SELECT riot_id FROM leagueconfig WHERE user_id = %s", (ctx.author.id,))
            if data:
                return await ctx.send(f"✅ Sua conta do LoL vinculada atualmente é: `{data['riot_id']}`")
            else:
                return await ctx.send(f"❌ Você não tem uma conta do LoL vinculada. Use `{ctx.prefix}linkleague Nome#TAG` para vincular.")

        if "#" not in riot_id:
            return await ctx.send("❌ Use o formato correto: `Nome#TAG` (ex: Grok#BR1)")

        await bot.db.execute("""
            INSERT INTO leagueconfig (user_id, riot_id) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE riot_id = %s
        """, (ctx.author.id, riot_id, riot_id))

        await ctx.send(f"✅ Conta `{riot_id}` vinculada com sucesso!")