import os
import importlib
import inspect
from discord.ext import commands

def setup_commands(bot):

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"Esse comando não existe. Digite `{ctx.prefix}help` para ver a lista de comandos.", delete_after=5)

    commands_dir = os.path.dirname(os.path.abspath(__file__))
    loaded_count = 0

    # Percorre recursivamente todas as pastas dentro de commands
    for root, dirs, files in os.walk(commands_dir):
        for file in sorted(files):
            # Ignora arquivos de sistema, __init__, o próprio handler e utils sem comandos
            if not file.endswith(".py") or file.startswith("__") or file == "commandshandler.py" or file.endswith("_utils.py"):
                continue

            # Monta o nome do módulo (ex: commands.admin.ban)
            rel_path = os.path.relpath(os.path.join(root, file), os.path.dirname(commands_dir))
            module_name = rel_path.replace(os.path.sep, ".").replace(".py", "")

            try:
                module = importlib.import_module(module_name)
                loaded = False

                # Procura a função de registro (setup_* ou com nome do comando) definida no próprio módulo
                for name, func in inspect.getmembers(module, inspect.isfunction):
                    if func.__module__ != module.__name__:
                        continue

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

                if not loaded:
                    print(f"[INFO] Nenhum setup de comando detectado em: {module_name}")

            except Exception as e:
                print(f"[ERRO] Erro ao carregar o modulo '{module_name}': {e}")

    print(f"[SUCESSO] Total de {loaded_count} comandos/modulos carregados automaticamente!")
