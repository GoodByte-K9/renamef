import argparse
import subprocess

from file_reader import list_files, read_file
from renamer import rename_files
from llm_client import Assistant
from tool_results import Result
from config import CONFIG
from texts import *
import prompts

paths_dict: dict[str, list] = {}


def _help(_help: bool = False):
    print(help_command_list)


def listf(path: str, recursive: bool = False, save: bool = False) -> str | None:
    global paths_dict

    if not recursive:
        list_result: Result = list_files(path)
    else:
        list_result: Result = list_files(path, recursive_listing=True)
    if issue := list_result.text:
        print(issue)
        return None
    if save:
        paths_dict = list_result.paths
    for key in list_result.paths:
        for item in list_result.paths[key]:
            print(item)
    return None


def summf(file_path: str, expand: bool = False, thinking: bool = False) -> None:
    llm = Assistant(thinking=thinking)
    instruction_seed: str = prompts.summf + file_path
    if expand:
        instruction = instruction_seed + prompts.summf_expand
    else:
        instruction = instruction_seed + prompts.summf_default

    print("Reading the document and contriving a summary...")
    response = llm.chat(instruction)
    print(response)
    subprocess.Popen(
        ["ollama", "stop", CONFIG["llm"]["model"]],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)


def renamef(file_path: str = "", new_name: str = "", fetch: bool = False, _all: bool = False, recursive: bool = False):
    ...


def _exit():
    ...


def parse_arguments(command: list[str]) -> None:
    args = parser.parse_args(command)
    if args.command == "help":
        commands["help"]()
    elif args.command == "listf":
        commands["listf"](path=args.path.strip('"'), recursive=args.recursive, save=args.save)
    elif args.command == "summf":
        commands["summf"](file_path=args.path.strip('"'), expand=args.expand, thinking=args.thinking)
    elif args.command == "renamef":
        if args.recursive and args.all is False:
            renamef_parser.error("'--recursive' only works with '--all'")  # Exits function because it raises SystemExit
        commands["renamef"](file_path=args.path.strip('"'), new_name=args.new_name, fetch=args.fetch,
                            _all=args.all, recursive=args.recursive)
    elif args.command == "exit":
        ...


parser = argparse.ArgumentParser(prog="")  # Empty string removes misguiding app name from help's "usage:" section
subparsers = parser.add_subparsers(dest="command")

help_parser = subparsers.add_parser("help", description="List available commands.")

listf_parser = subparsers.add_parser("listf", description=help_listf)
listf_parser.add_argument("path", metavar="PATH")
listf_parser.add_argument("-r", "--recursive", action="store_true", help=listf_recursive_arg)
listf_parser.add_argument("-s", "--save", action="store_true", help=listf_save_arg)

summf_parser = subparsers.add_parser("summf", description=help_summf)
summf_parser.add_argument("path", metavar="PATH")
summf_parser.add_argument("-e", "--expand", action="store_true", help=summf_expand_arg)
summf_parser.add_argument("-t", "--thinking", action="store_true", help=summf_thinking_arg)

renamef_parser = subparsers.add_parser("renamef", description=help_renamef)
renamef_parser.add_argument("path", metavar="PATH")
renamef_parser.add_argument("new_name", metavar="NEW_NAME", nargs="?")  # value=None if left empty
solitary_fetch = renamef_parser.add_mutually_exclusive_group()
solitary_fetch.add_argument("-f", "--fetch", action="store_true", help=renamef_fetch_arg)
solitary_fetch.add_argument("-a", "--all", action="store_true", help=renamef_all_arg)
renamef_parser.add_argument("-r", "--recursive", action="store_true", help=renamef_recursive_arg)

commands = {
    "help": _help,
    "listf": listf,
    "summf": summf,
    "renamef": renamef,
    "exit": _exit,
    "quit": _exit,
}
