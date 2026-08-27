import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import time
import random

active_giveaways = {}
_giveaways_restored = False

UNIT_MULTIPLIERS = {
    "segundos": 1,
    "segundo": 1,
    "s": 1,
    "minutos": 60,
    "minuto": 60,
    "m": 60,
    "min": 60,
    "horas": 3600,
    "hora": 3600,
    "h": 3600,
    "dias": 86400,
    "dia": 86400,
    "d": 86400,
    "meses": 86400 * 30,
    "mes": 86400 * 30,
    "mês": 86400 * 30,
    "mo": 86400 * 30,
}

def setup_giveaway_command(bot):

    def build_help_embed(prefix):
        embed = discord.Embed(
            title="🎉 Como criar um Sorteio",
            description="Para iniciar um sorteio, forneça todos os parâmetros necessários:",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="📌 Sintaxe com Prefixo",
            value=f"`{prefix}giveaway <#canal> \"<título>\" \"<descrição>\" <tempo> <medida>`",
            inline=False
        )
        embed.add_field(
            name="⚡ Sintaxe com Slash Command",
            value="`/giveaway canal:#canal titulo:... descricao:... tempo:... medida:...`",
            inline=False
        )
        embed.add_field(
            name="⏱️ Unidades de Medida Aceitas",
            value="`segundos`, `minutos`, `horas`, `dias`, `meses`",
            inline=False
        )
        embed.add_field(
            name="💡 Exemplos de Uso",
            value=(
                f"• `{prefix}giveaway #sorteios \"Nitro Mensal\" \"Sorteio para os membros\" 30 minutos`\n"
                f"• `{prefix}giveaway #geral \"Cargo VIP\" \"Reaja com 🎉 para participar!\" 2 dias`"
            ),
            inline=False
        )
        embed.set_footer(text="Requer permissão de Gerenciar Mensagens.")
        return embed

    def build_giveaway_embed(title, description, end_timestamp, host_mention, participant_count, is_ended=False, winner_mention=None):
        if is_ended:
            embed = discord.Embed(
                title=f"🎉 SORTEIO ENCERRADO: {title} 🎉",
                description=description,
                color=discord.Color.green() if winner_mention else discord.Color.red()
            )
            if winner_mention:
                embed.add_field(name="🏆 Vencedor(a)", value=winner_mention, inline=False)
            else:
                embed.add_field(name="🏆 Vencedor(a)", value="Nenhum participante.", inline=False)

            embed.add_field(name="👥 Total de Participantes", value=f"`{participant_count}`", inline=True)
            embed.add_field(name="👑 Criado por", value=host_mention, inline=True)
            embed.set_footer(text="Sorteio finalizado")
        else:
            embed = discord.Embed(
                title=f"🎉 SORTEIO: {title} 🎉",
                description=description,
                color=discord.Color.gold()
            )
            embed.add_field(
                name="⏱️ Termina em",
                value=f"<t:{end_timestamp}:R> (<t:{end_timestamp}:F>)",
                inline=False
            )
            embed.add_field(name="👥 Participantes", value=f"**{participant_count}** pessoas", inline=True)
            embed.add_field(name="👑 Criado por", value=host_mention, inline=True)
            embed.set_footer(text="Reaja com 🎉 abaixo para participar ou desmarque para sair!")
            
        return embed

    async def update_giveaway_embed(message, data):
        try:
            embed = build_giveaway_embed(
                title=data['title'],
                description=data['description'],
                end_timestamp=data['end_time'],
                host_mention=f"<@{data['host_id']}>",
                participant_count=len(data['participants']),
                is_ended=False
            )
            await message.edit(embed=embed)
        except Exception as e:
            print(f"[GIVEAWAY] Erro ao atualizar embed em tempo real: {e}")

    async def finish_giveaway(message_id):
        if message_id not in active_giveaways:
            return

        data = active_giveaways.pop(message_id)
        guild = bot.get_guild(data['guild_id'])
        if not guild:
            return

        channel = guild.get_channel(data['channel_id'])
        if not channel:
            return

        try:
            message = await channel.fetch_message(message_id)
        except Exception:
            message = None

        participants = list(data['participants'])
        winner_id = None
        winner_mention = None

        if participants:
            winner_id = random.choice(participants)
            winner_mention = f"<@{winner_id}>"

        try:
            await bot.db.execute("""
                UPDATE giveaways 
                SET ended = TRUE, winner_id = %s 
                WHERE message_id = %s
            """, (winner_id, message_id))
        except Exception as e:
            print(f"[GIVEAWAY] Erro ao atualizar banco no término: {e}")

        if message:
            try:
                ended_embed = build_giveaway_embed(
                    title=data['title'],
                    description=data['description'],
                    end_timestamp=data['end_time'],
                    host_mention=f"<@{data['host_id']}>",
                    participant_count=len(participants),
                    is_ended=True,
                    winner_mention=winner_mention
                )
                await message.edit(embed=ended_embed)
            except Exception as e:
                print(f"[GIVEAWAY] Erro ao editar mensagem final: {e}")

        if winner_id:
            await channel.send(
                f"🎉 Parabéns {winner_mention}! Você ganhou o sorteio de **{data['title']}**! 🏆"
            )
        else:
            await channel.send(f"😢 O sorteio de **{data['title']}** foi encerrado, mas ninguém participou.")

    async def giveaway_timer(message_id, wait_seconds):
        if wait_seconds > 0:
            await asyncio.sleep(wait_seconds)
        await finish_giveaway(message_id)

    # ----------------------------------------------------
    # COMANDO /giveaway
    # ----------------------------------------------------
    @bot.hybrid_command(
        name="giveaway",
        aliases=["sorteio"],
        description="Inicia um sorteio no servidor"
    )
    @app_commands.describe(
        canal="Canal de texto onde o sorteio será publicado",
        titulo="Título ou prêmio do sorteio",
        descricao="Descrição e regras do sorteio",
        tempo="Quantidade de tempo (número)",
        medida="Unidade de medida de tempo"
    )
    @app_commands.choices(medida=[
        app_commands.Choice(name="Segundos", value="segundos"),
        app_commands.Choice(name="Minutos", value="minutos"),
        app_commands.Choice(name="Horas", value="horas"),
        app_commands.Choice(name="Dias", value="dias"),
        app_commands.Choice(name="Meses", value="meses"),
    ])
    @commands.has_permissions(manage_messages=True)
    async def giveaway(ctx, canal: discord.TextChannel = None, titulo: str = None, descricao: str = None, tempo: float = None, medida: str = "dias"):
        # Se o usuário mandou apenas !giveaway ou faltou algum parâmetro
        if canal is None or titulo is None or descricao is None or tempo is None:
            return await ctx.send(embed=build_help_embed(ctx.prefix), ephemeral=True)

        await ctx.defer(ephemeral=True)

        unit = medida.lower().strip()
        multiplier = UNIT_MULTIPLIERS.get(unit)
        if not multiplier:
            return await ctx.send("❌ Unidade de medida inválida! Escolha entre: `segundos`, `minutos`, `horas`, `dias` ou `meses`.", ephemeral=True)

        if tempo <= 0:
            return await ctx.send("❌ O tempo deve ser um número maior que zero (ex: `30` segundos, `10` minutos, `2` horas, `3` dias).", ephemeral=True)

        duration_seconds = int(tempo * multiplier)
        end_timestamp = int(time.time() + duration_seconds)

        embed = build_giveaway_embed(
            title=titulo,
            description=descricao,
            end_timestamp=end_timestamp,
            host_mention=ctx.author.mention,
            participant_count=0,
            is_ended=False
        )

        try:
            giveaway_msg = await canal.send(embed=embed)
            await giveaway_msg.add_reaction("🎉")
        except discord.Forbidden:
            return await ctx.send(f"❌ Não tenho permissão para enviar mensagens ou reações no canal {canal.mention}.", ephemeral=True)

        try:
            await bot.db.execute("""
                INSERT INTO giveaways (message_id, channel_id, guild_id, title, description, end_time, host_id, ended)
                VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)
            """, (giveaway_msg.id, canal.id, ctx.guild.id, titulo, descricao, end_timestamp, ctx.author.id))
        except Exception as e:
            print(f"[GIVEAWAY] Erro ao salvar sorteio no banco: {e}")

        active_giveaways[giveaway_msg.id] = {
            'channel_id': canal.id,
            'guild_id': ctx.guild.id,
            'title': titulo,
            'description': descricao,
            'end_time': end_timestamp,
            'host_id': ctx.author.id,
            'participants': set()
        }

        asyncio.create_task(giveaway_timer(giveaway_msg.id, duration_seconds))
        await ctx.send(f"✅ Sorteio de **{titulo}** iniciado com sucesso no canal {canal.mention}!", ephemeral=True)

    @giveaway.error
    async def giveaway_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você precisa da permissão de `Gerenciar Mensagens` para criar sorteios.", ephemeral=True)
        elif isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
            await ctx.send(embed=build_help_embed(ctx.prefix), ephemeral=True)

    # ----------------------------------------------------
    # EVENTOS DE REAÇÃO EM TEMPO REAL
    # ----------------------------------------------------
    @bot.listen("on_raw_reaction_add")
    async def on_raw_reaction_add(payload):
        if bot.user and payload.user_id == bot.user.id:
            return
        if str(payload.emoji) != "🎉":
            return
        if payload.message_id not in active_giveaways:
            return

        data = active_giveaways[payload.message_id]
        if payload.user_id not in data['participants']:
            data['participants'].add(payload.user_id)
            
            channel = bot.get_channel(payload.channel_id)
            if channel:
                try:
                    msg = await channel.fetch_message(payload.message_id)
                    await update_giveaway_embed(msg, data)
                except Exception as e:
                    print(f"[GIVEAWAY] Erro ao atualizar no reaction add: {e}")

    @bot.listen("on_raw_reaction_remove")
    async def on_raw_reaction_remove(payload):
        if bot.user and payload.user_id == bot.user.id:
            return
        if str(payload.emoji) != "🎉":
            return
        if payload.message_id not in active_giveaways:
            return

        data = active_giveaways[payload.message_id]
        if payload.user_id in data['participants']:
            data['participants'].discard(payload.user_id)
            
            channel = bot.get_channel(payload.channel_id)
            if channel:
                try:
                    msg = await channel.fetch_message(payload.message_id)
                    await update_giveaway_embed(msg, data)
                except Exception as e:
                    print(f"[GIVEAWAY] Erro ao atualizar no reaction remove: {e}")

    # ----------------------------------------------------
    # RECUPERAÇÃO DE SORTEIOS ATIVOS AO LIGAR O BOT
    # ----------------------------------------------------
    async def restore_active_giveaways():
        global _giveaways_restored
        if _giveaways_restored:
            return
        _giveaways_restored = True
        
        await bot.wait_until_ready()
        await asyncio.sleep(2)
        try:
            rows = await bot.db.fetch("SELECT * FROM giveaways WHERE ended = FALSE")
            now = time.time()
            for row in rows:
                msg_id = row['message_id']
                channel_id = row['channel_id']
                end_time = row['end_time']
                
                channel = bot.get_channel(channel_id)
                participants = set()

                if channel:
                    try:
                        msg = await channel.fetch_message(msg_id)
                        for reaction in msg.reactions:
                            if str(reaction.emoji) == "🎉":
                                async for user in reaction.users():
                                    if not user.bot:
                                        participants.add(user.id)
                    except Exception as err:
                        print(f"[GIVEAWAY] Não foi possível ler mensagem do sorteio {msg_id}: {err}")

                active_giveaways[msg_id] = {
                    'channel_id': channel_id,
                    'guild_id': row['guild_id'],
                    'title': row['title'],
                    'description': row['description'],
                    'end_time': end_time,
                    'host_id': row['host_id'],
                    'participants': participants
                }

                remaining = max(0, int(end_time - now))
                asyncio.create_task(giveaway_timer(msg_id, remaining))
                print(f"[GIVEAWAY] Sorteio '{row['title']}' restaurado ({len(participants)} participantes, restam {remaining}s).")
        except Exception as e:
            print(f"[GIVEAWAY] Erro ao restaurar sorteios ativos: {e}")

    @bot.listen("on_ready")
    async def _on_giveaway_ready():
        await restore_active_giveaways()
