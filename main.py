import discord
from discord.ext import commands
from triggers.messageTriggers import message_triggers
from dotenv import load_dotenv
from commands.commandshandler import setup_commands
from database import Database
import os
import shutil
load_dotenv()

async def get_prefix(bot, message):
    if not message.guild:
        return "."
    return bot.prefix_cache.get(message.guild.id, ".")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.voice_states = True

bot = commands.Bot(command_prefix=get_prefix, intents=intents, case_insensitive=True, help_command=None)
bot.prefix_cache = {}

async def setup_hook():
    bot.db = Database()
    await bot.db.setup()
    await bot.db.create_tables()
    
    try:
        rows = await bot.db.fetch("SELECT guild_id, serverprefix FROM botsettings")
        for row in rows:
            bot.prefix_cache[row['guild_id']] = row['serverprefix']
        print(f"[CACHE] {len(bot.prefix_cache)} servidores configurados carregados.")
    except Exception as e:
        print(f"[CACHE] Erro ao carregar caches no startup: {e}")

    # Sincroniza os Slash Commands com o Discord
    try:
        synced = await bot.tree.sync()
        print(f"[SLASH] {len(synced)} Slash Commands sincronizados com o Discord!")
    except Exception as e:
        print(f"[SLASH] Erro ao sincronizar Slash Commands: {e}")

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    print(f"[BOT] Loguei como {bot.user}")
    downloads_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloadedsongs")
    try:
        if os.path.exists(downloads_folder):
            shutil.rmtree(downloads_folder)
        os.makedirs(downloads_folder)
        print(f"[CLEANUP] Pasta '{downloads_folder}' reiniciada com sucesso ao iniciar.")
    except Exception as e:
        print(f"[CLEANUP] Erro ao limpar pasta de downloads no on_ready: {e}")

setup_commands(bot)
message_triggers(bot)

if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))
