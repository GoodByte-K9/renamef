from file_reader import list_files, read_file
from renamer import rename_files


def show_help():
    print("""
    help - Show the help page with all commands listed and described.
    list - 
    read - 
    rename -  
    """)


commands = {
    "help": show_help,
    "list-files": list_files,
    "read-file": read_file,
    "rename": rename_files,
    "exit": "func",
}
