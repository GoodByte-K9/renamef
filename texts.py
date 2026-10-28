
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

install_confirmation = ("\nNo installation found. Ollama is required for the app to work in its intended way.\n"
                        "Download and install Ollama now? (yes/no)\n")

install_warning = "Ollama is required for the application to work. Exiting application..."

# ------------------------------ HELP ------------------------------ #
help_command_list = """
    help - List available commands.
    listf - List all files in a location.
    summf - Summarize file contents.
    renamef -  Rename a given file or files.
    exit - Exit the application.
    
    Run <command> -h/--help for more details.
    """

# ------------------------------ LISTF ------------------------------ #
help_listf = r"""List all files in a location. PATH represents an absolute file path of your choice. Wrap the path in 
double quotes ("") when writing the command. Only the following files will be listed: 
pdf, txt, md, png, jpeg, jpg, webp, gif."""
listf_recursive_arg = """List all files recursively from all subfolders in a given "PATH".
Use quotation marks around the path."""
listf_save_arg = "Save the result for LLM."
listf_epilog = r"""Examples:
listf -rs "C:\Users\Public\Documents"
"""

# ------------------------------ SUMMF ------------------------------ #
help_summf = """Instruct an LLM to read a file and summarize it for you. Attempts to exclude personally identifiable
information. Thinking off by default. PATH represents an absolute file path of your choice. Wrap the path in double 
quotes ("") when writing the command. Only the following files are supported: pdf, txt, md, png, jpeg, jpg, webp, gif.
"""
summf_expand_arg = """Increase the amount of content the LLM reads from pdf, txt, and md files to help with context
comprehension. This option may slow down the process."""
summf_thinking_arg = "Enable thinking for the model. This option may slow down the process."
summf_epilog = r"""Examples:
summarize -et "C:\Users\Public\Documents\cryptic_secrets.txt"
"""

# ------------------------------ RENAMEF ------------------------------ #
help_renamef = """Instruct an LLM to rename all files in a given PATH. Alternatively, point the LLM to a specific 
file to rename it based on its contents. PATH represents an absolute file path of your choice. Wrap the path 
in double quotes ("") when writing the command."""

renamef_fetch_arg = """Fetch a file list from previously run listf -s to the LLM. Renames all files in the list.
Does not work with "PATH" or -r/--recursive."""
renamef_recursive_arg = "Include files in subfolders. Does not work with -f/--fetch."
renamef_thinking_arg = "Enable thinking for the model. This option may slow down the process."
renamef_epilog = r'''Examples:
renamef -tr "C:\Users\Public\Documents"
renamef -ft
renamef "C:\Users\Public\Documents\1234567.txt"
'''

# ------------------------------ EXIT ------------------------------ #
help_exit = r"""Usage: exit
or: quit
Exit the application.

Example:
exit
"""