import json
import argparse
import subprocess
from dataclasses import asdict

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


def renamef(file_path: str | None = "",
            new_name: str | None = "",
            fetch: bool = False,
            _all: bool = False,
            recursive: bool = False) -> None:

    def extract_results(result: Result):
        text: str = result.text
        change_log: list = result.change_log
        return text, change_log

    # User initiated file renaming
    if file_path and new_name:
        file_to_rename = [{"original_path": file_path, "new_name": new_name}]
        # rename the file and extract results
        r_text, r_change_log = extract_results(rename_files(file_to_rename, llm=False))
        log_str = "\n".join(r_change_log)

        rnm_reply = r_text if not None else log_str
        print(rnm_reply)
        return

    file_list = None

    if fetch and file_path is None and new_name is None:
        fetch = fetch if any(paths_dict.values()) else False  # fetch_dict can only be True if paths_dict is not empty
        if fetch is False:
            print("Error: Failed to fetch file list. File list was empty...")
            return
        else:
            file_list = json.dumps(paths_dict)

    # LLM initiated file renaming
    if _all and file_path:
        file_list = json.dumps(asdict(list_files(file_path, recursive)))  # Result -> Dict -> JSON

    if file_list is not None:
        llm = Assistant()
        llm.chat(prompts.renamef_default + "PUT THE FILE NAME FROM THE LOOP HERE")


# Generate new Assistant object and loop across the whole list, one by one, asking the LLM to rename the file.
# this resets the context window, while also giving specific instructions (next file to check in loop) to the LLM, so
# no memory is even needed.

# _all workflow
# - Get a list of files programmatically to save context memory
# - Create a loop that iterates n number of times based on number of values in file_list
# - Initiate LLM...

# 1. System -> instructions
# 2. User -> rename a specific file (item from the loop)
# 3. Assistant -> call read_file()
# 4. Tool -> returns file text
# 5. Assistant -> call rename_files() on that 1 file
# 6. Tool -> renames the file
# 7. Assistant -> Returns logs to user

# Rinse and repeat until loop is done
# Requires moving user confirmation away from rename_files...
# TODO: Move user confirmation message from rename_files()


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
        commands["renamef"](file_path=args.path.strip('"'), new_name=args.new_name.strip('"'), fetch=args.fetch,
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
renamef_parser.add_argument("path", metavar="PATH", nargs="?")
excl_renamef_args = renamef_parser.add_mutually_exclusive_group()
excl_renamef_args.add_argument("new_name", metavar="NEW_NAME", nargs="?")  # value=None if left empty
excl_renamef_args.add_argument("-f", "--fetch", action="store_true", help=renamef_fetch_arg)
excl_renamef_args.add_argument("-a", "--all", action="store_true", help=renamef_all_arg)
renamef_parser.add_argument("-r", "--recursive", action="store_true", help=renamef_recursive_arg)

commands = {
    "help": _help,
    "listf": listf,
    "summf": summf,
    "renamef": renamef,
    "exit": _exit,
    "quit": _exit,
}
