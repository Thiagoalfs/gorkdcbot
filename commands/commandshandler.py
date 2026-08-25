import os
import sys
import importlib
import inspect
import traceback
from discord.ext import commands

def setup_commands(bot):

    @bot.listen("on_command_error")
    async def on_command_error(ctx, error):
        # Se o comando tiver um tratamento de erro local definido (ex: @ban.error), deixa ele tratar
        if hasattr(ctx.command, "on_error"):
            return

        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"Esse comando não existe. Digite `{ctx.prefix}help` para ver a lista de comandos.", delete_after=5)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você não tem permissão para executar este comando.", delete_after=5)
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("❌ Você não atende aos requisitos para usar este comando.", delete_after=5)
        else:
            print(f"[ERRO DE EXECUÇÃO] Comando '{ctx.command}' no servidor {ctx.guild} falhou: {error}")
            traceback.print_exception(type(error), error, error.__traceback__)

    commands_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(commands_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    loaded_count = 0

    # Percorre recursivamente todas as pastas dentro de commands
    for root, dirs, files in os.walk(commands_dir):
        for file in sorted(files):
            # Ignora arquivos de sistema, __init__, o próprio handler e utils sem comandos
            if not file.endswith(".py") or file.startswith("__") or file == "commandshandler.py" or file.endswith("_utils.py"):
                continue

            # Monta o nome do módulo compatível com qualquer SO (ex: commands.songs.vcplay)
            rel_path = os.path.relpath(os.path.join(root, file), project_root)
            module_name = rel_path.replace("\\", ".").replace("/", ".").replace(".py", "")

            try:
                module = importlib.import_module(module_name)
                loaded = False

                # Coleta funções definidas no próprio módulo
                funcs = [
                    (name, func) for name, func in inspect.getmembers(module, inspect.isfunction)
                    if func.__module__ == module.__name__
                ]

                # Prioriza funções que começam com 'setup', depois nome do arquivo, depois com parâmetro 'bot'
                def sort_key(item):
                    name, _ = item
                    file_stem = file[:-3]
                    if name == "setup" or name == f"setup_{file_stem}" or name.startswith("setup"):
                        return 0
                    if name == file_stem or name.replace("_", "") == file_stem.replace("_", ""):
                        return 1
                    return 2

                funcs.sort(key=sort_key)

                for name, func in funcs:
                    try:
                        sig = inspect.signature(func)
                        params = list(sig.parameters.keys())
                        if len(params) == 1 and (
                            name.startswith("setup")
                            or "bot" in params
                            or name == file[:-3]
                            or name.replace("_", "") == file[:-3].replace("_", "")
                        ):
                            func(bot)
                            loaded = True
                            loaded_count += 1
                            print(f"[COMANDO] Carregado: {module_name} -> {name}()")
                            break
                    except Exception as err:
                        print(f"[AVISO] Erro ao inspecionar {name} em {module_name}: {err}")
                        traceback.print_exc()

                if not loaded:
                    print(f"[INFO] Nenhum setup de comando detectado em: {module_name}")

            except Exception as e:
                print(f"[ERRO] Falha crítica ao carregar módulo '{module_name}': {e}")
                traceback.print_exc()

    print(f"[SUCESSO] Total de {loaded_count} comandos/módulos carregados com sucesso!")

