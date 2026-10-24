from texts import command_list, help_help, help_listf, help_summf, help_renamef, help_exit
from file_reader import list_files, read_file
from renamer import rename_files
from tool_results import Result

paths_dict: dict[str, list] = {}


def _help(_help: bool = False):
    print(command_list)


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


def summf(file_path: str, expand: bool = False, thinking: bool = False):
    ...


def renamef(file_path: str = "", fetch: bool = False, _all: bool = False, recursive: bool = False):
    ...


def _exit():
    ...


commands = {
    "help": _help,
    "listf": listf,
    "summf": summf,
    "renamef": renamef,
    "exit": _exit,
    "quit": _exit,
}
