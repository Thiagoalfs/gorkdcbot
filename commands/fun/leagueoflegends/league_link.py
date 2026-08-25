from discord.ext import commands

def setup_league_link_command(bot):
    @bot.hybrid_command(
        name="leaguelink", 
        aliases=["vincularlol", "linkleague", "lollink", "linklol"],
        description="Vincula sua conta Riot (Nome#TAG) ao seu usuário do Discord"
    )
    async def linkleague(ctx, *, riot_id: str = None):
        if riot_id is None:
            data = await bot.db.fetch_one("SELECT riot_id FROM leagueconfig WHERE user_id = %s", (ctx.author.id,))
            if data:
                return await ctx.send(f"✅ Sua conta do LoL vinculada atualmente é: `{data['riot_id']}`")
            else:
                return await ctx.send(f"❌ Você não tem uma conta vinculada. Use `{ctx.prefix}leaguelink Nome#TAG`.")

        if "#" not in riot_id:
            return await ctx.send("❌ Use o formato correto: `Nome#TAG` (ex: Grok#BR1)", ephemeral=True)

        await bot.db.execute("""
            INSERT INTO leagueconfig (user_id, riot_id) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE riot_id = %s
        """, (ctx.author.id, riot_id, riot_id))

        await ctx.send(f"✅ Conta `{riot_id}` vinculada com sucesso!")
