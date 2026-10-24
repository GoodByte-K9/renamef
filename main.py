import shlex
import shutil
import platform


from llm_client import Assistant
from commands import parse_arguments
from texts import *
import ollama

assistant = Assistant()
running = True

print(f"{art}\n{welcome}")

ollama_path = shutil.which("ollama")
if ollama_path is None:
    while True:
        install_confirmation = input(install_confirmation)
        if install_confirmation in ["yes", "y"]:
            ollama.install()
            break
        elif install_confirmation in ["no", "n"]:
            print(install_warning)
            running = False
            break
        else:
            print("Invalid answer...")

ollama.server()
ollama.pull_model()

# Must specify POSIX for shlex, lest it fail at reading paths with backslashes
is_posix = False if platform.system() == "Windows" else True
while running:
    user_input = shlex.split(input("> "), posix=is_posix)
    try:
        parse_arguments(user_input)
    except SystemExit:
        pass
