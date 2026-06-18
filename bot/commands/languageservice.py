import os, json

async def languageservice(bot, ctx, commandpath, jsonfile):
    # Define a linguagem padrão
    lang_code = "en"

    if ctx.guild:
        # Busca diretamente do cache para economizar conexões com o banco
        lang_code = bot.lang_cache.get(ctx.guild.id, "EN").lower()
    
    json_path = os.path.join(os.path.dirname(__file__), "..", "languages", lang_code, commandpath, jsonfile)
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            responses = json.load(f)
            return responses
    except Exception as e:
        print(f"❌ Erro ao carregar traduções ({lang_code}/{jsonfile}): {e}")
        return None