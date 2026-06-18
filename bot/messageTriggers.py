from mentionTriggers import mention_triggers

def message_triggers(bot):
    @bot.event
    async def on_ready():
        print(f"Loguei como {bot.user}")

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return True
        
        await bot.process_commands(message)
            
        await mention_triggers(bot, message)
                        