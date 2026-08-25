from triggers.mentionTriggers import mention_triggers

def message_triggers(bot):
    @bot.event
    async def on_ready():
        print(f"[BOT] Message triggers prontos para {bot.user}")

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return
        
        await bot.process_commands(message)
        await mention_triggers(bot, message)
