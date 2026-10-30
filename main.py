import shlex
import shutil
import platform
import sys

from llm_client import Assistant
from commands import parse_arguments
import ollama
import texts

assistant = Assistant()
running = True
app_response = ""
ollama_server = None

print("checking if Ollama is installed...")
if shutil.which("ollama") is None:
    while True:
        install_confirmation = input(texts.install_confirmation)
        if install_confirmation in ["yes", "y"]:
            ollama.install()
            break
        elif install_confirmation in ["no", "n"]:
            print(f"\n{texts.install_warning}\n")
            sys.exit()
        else:
            print("Invalid answer...")

ollama_server = ollama.server()
ollama.pull_model()
print(f"{texts.art}\n{texts.welcome}")

# Must specify POSIX for shlex, lest it fail at reading paths with backslashes
is_posix = False if platform.system() == "Windows" else True
try:
    while running:
        user_input = shlex.split(input("\n> "), posix=is_posix)
        try:
            app_response = parse_arguments(user_input)
        except SystemExit:
            pass
        if app_response == "exit":
            print("")
            break
except KeyboardInterrupt:
    print("Exiting...\n")
    sys.exit()
finally:
    if ollama_server is not None:
        ollama.terminate_process(ollama_server)
