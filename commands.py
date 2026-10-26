import argparse
import subprocess
from pathlib import Path

from file_reader import list_files, read_file
from renamer import rename_files
from llm_client import Assistant
from tool_results import Result
from config import CONFIG
from texts import *
import prompts

paths_dict: dict[str, list] = {}


def stop_model():
    subprocess.Popen(
        ["ollama", "stop", CONFIG["llm"]["model"]],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)


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
    stop_model()


def renamef(file_path: str | None,
            new_name: str | None,
            fetch: bool = False,
            recursive: bool = False) -> None:

    def extract_results(result: Result):
        text: str = result.text
        change_log: list = result.change_log
        return text, change_log

    def green_light(dict_of_files: dict[str, list]) -> bool:
        file_counter = 0
        listed_files = 0
        print_limit = 20
        file_scan_limit = print_limit + 200
        print(f"Following files will be renamed based on their content:\n")
        for a_list in dict_of_files.values():
            for a_file in a_list:
                if file_counter <= print_limit:
                    print({a_file})
                    listed_files += 1
                file_counter += 1
                if file_counter > file_scan_limit:
                    break
            if file_counter > file_scan_limit:
                break
        if file_counter > file_scan_limit:
            print(f"+ over {file_counter - listed_files} files to rename... This might take a while")
        elif file_counter <= listed_files:
            pass
        else:
            print(f"+ {file_counter - listed_files} files to rename.")
        while True:
            user_confirmation = input("Do you wish to proceed? (yes/no)\n")
            if user_confirmation.lower() in ["yes", "y"]:
                print("List accepted. Proceeding to execute the plan...")
                return True
            elif user_confirmation.lower() == ["no", "n"]:
                print("Process interrupted...")
                return False
            else:
                print("Warning: Only a yes/y or a no/n is accepted as an answer.")

    # User initiated file renaming
    if file_path and new_name:
        file_to_rename = [{"original_path": file_path.strip('"'), "new_name": new_name}]
        # rename the file and extract results
        r_text, r_change_log = extract_results(rename_files(file_to_rename))
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
            file_list = paths_dict

    if file_path or file_path and new_name is None and not fetch:
        if Path(file_path.strip('"')).is_file():
            file_list = {"specific_file": [file_path]}
        else:
            file_list = list_files(file_path.strip('"'), recursive).paths  # Result -> Dict

    if file_list is not None:
        if not green_light(file_list):  # Confirm from user whether the list of files should be renamed
            return
        print("Initiating task...")
        llm = Assistant()  # Left outside the loop so a new API client is not created on each iteration -> shaves time
        print("Changes will be listed below: ")
        for _list in file_list.values():
            for file in _list:
                print(llm.chat(prompts.renamef_default + file))
                llm.reset_history()  # Clear so context window doesn't get out of hand

    stop_model()


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
            renamef_parser.error("'--recursive' only works with ...")  # Exits function because it raises SystemExit
        commands["renamef"](file_path=args.path, new_name=args.new_name, fetch=args.fetch, recursive=args.recursive)
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
excl_renamef_args.add_argument("-r", "--recursive", action="store_true", help=renamef_recursive_arg)

commands = {
    "help": _help,
    "listf": listf,
    "summf": summf,
    "renamef": renamef,
    "exit": _exit,
    "quit": _exit,
}
