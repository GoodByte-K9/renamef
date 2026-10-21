import shutil

from texts import art, welcome, install_confirmation, install_warning
from llm_client import Assistant
from commands import commands
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
else:
    ollama_server = ollama.server()

while running:
    user_input = input("> ").split(" ")
    if user_input[0] in commands:
        print(commands[user_input[0]])
