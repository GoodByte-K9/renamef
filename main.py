import shlex
import shutil
import platform
import argparse

from llm_client import Assistant
from commands import commands
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
else:
    ollama.server()

    parser = argparse.ArgumentParser(prog="rnm")
    subparsers = parser.add_subparsers(dest="command")
    # add_parser() registers "listf" as a command
    listf_parser = subparsers.add_parser("listf", description=help_listf)
    listf_parser.add_argument("path")  # create attribute named "path" where user input is stored (positional argument)
    listf_parser.add_argument("-r", "--recursive", action="store_true", help=listf_recursive_arg)
    listf_parser.add_argument("-s", "--save", action="store_true", help=listf_save_arg)


def parse_arguments(command: list[str]):
    args = parser.parse_args(command)
    if args.command == "help":
        commands["help"](args.help)
    elif args.command == "listf":
        commands["listf"](args.recursive, args.save, args.path)
    elif args.command == "summf":
        ...


# Must specify POSIX for shlex, lest it fail at reading paths with backslashes
is_posix = False if platform.system() == "Windows" else True
while running:
    user_input = shlex.split(input("> "), posix=is_posix)
    try:
        parse_arguments(user_input)
    except SystemExit:
        pass
