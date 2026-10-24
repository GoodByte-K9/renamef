
art = r"""
        .-----------.
 ___    |           |
/_._`.__|           |_
    `(|_|_m_______m_|_|)
      |_______________|
      /o o o o o o o o\
     /o o o o o o o o o\
    ;[]o o o o o o o o[];
    |  -============-   |
     '------------------'
"""

welcome = """Welcome to File Renamer. Does what it says on the tin. LLM-powered for context comprehension.
Type "help" for commands."""

install_confirmation = ("\nOllama is required for the app to work in its intended way.\n"
                        "Download and install Ollama now? (yes/no)\n")

install_warning = "Ollama is required for the application to work. Exiting application..."

command_list = """
    help - List available commands.
    listf - List all files in a location .
    summf - Summarize file contents.
    renamef -  Rename a given file or files.
    exit - Exit the application.
    
    Run <command> --help for more details.
    """

help_help = r"""Usage: help [OPTIONS]
List available commands.

-h, --help                    Show details of the help command.

Example:
help -h
"""

help_listf = r"""List all files in a location. PATH represents an absolute path of your choice.
Only the following files are listed: pdf, txt, md, png, jpeg, jpg, webp, gif."""

listf_recursive_arg = ("List all files recursively from all subfolders in a given 'PATH'."
                       "Use quotation marks around the path.")
listf_save_arg = "Save the result for LLM."
# Usage: listf [OPTIONS] PATH
# -r, --recursive               List all files recursively from all subfolders in a given PATH
# -s, --save                    Save the result for LLM.
#
# Example:
# listf -rs 'C:\Users\Public\Documents'


help_summf = r"""Usage: summf [OPTIONS] PATH
Instruct an LLM to read a file and summarize it for you. Only the following files are supported: 
pdf, txt, md, png, jpeg, jpg, webp, gif. Thinking is off by default.

-e, --expand                  Increase the amount of text the LLM reads from pdf, txt, and md files.
                              This option slows down the process.
-t, --thinking                Enable thinking for the model. This option slows down the process.

Examples:
summarize -et 'C:\Users\Public\Documents\cryptic_secrets.txt'
"""

help_renamef = r"""Usage: renamef [OPTIONS] [PATH] [NEW-FILE-NAME]
or: renamef -l
Instruct an LLM to rename a given file based on file context. Give a path to a file, or load the results from listf to 
rename all files in the list. Only the following files are supported: pdf, txt, md, png, jpeg, jpg, webp, gif. 
Thinking is off by default.

-f, --fetch                   Fetch a file list from previously run listf to LLM. Renames all files in the list.
-a, --all                     Rename all files in a given folder based on file context.
-r, --recursive               Used with -a to include files in subfolders.

Examples:
renamef C:\Users\Public\Documents\cryptic_secrets.txt not_secret_anymore.txt
renamef -f
renamef -ar 'C:\Users\Public\Documents\'
"""

help_exit = r"""Usage: exit
or: quit
Exit the application.

Example:
exit
"""