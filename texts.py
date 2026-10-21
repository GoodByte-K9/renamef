
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

help_listf = r"""Usage: listf [OPTIONS] PATH
List all files in a location. Only the following files are listed: 
pdf, txt, md, png, jpeg, jpg, webp, gif.

-r, --recursive                 List all files recursively from all folders in the given PATH
-s, --save                      Save the result for LLM.

Example:
listf -r C:\Users\Public\Documents
"""

help_summf = r"""Usage: summf [OPTIONS] PATH
Instruct an LLM to read a file and summarize it for you. Only the following files are supported: 
pdf, txt, md, png, jpeg, jpg, webp, gif. Thinking is off by default.

-e, --expand                    Increase the amount of text the LLM reads from pdf, txt, and md files.
                                This option slows down the process.
-t, --thinking                  Enable thinking for the model. This option slows down the process.

Examples:
summarize -et C:\Users\Public\Documents\cryptic_secrets.txt
"""

help_renamef = r"""Usage: renamef PATH NEW-FILE-NAME
or: renamef -l
Instruct an LLM to rename a given file based of file context. Give a path to a file, or load the results from listf to  
rename all files in the list. Only the following files are supported: pdf, txt, md, png, jpeg, jpg, webp, gif. 
Thinking is off by default.

-l, --load                    Load a file list from listf to LLM. Renames all files in the list.

Examples:
renamef C:\Users\Public\Documents\cryptic_secrets.txt not_secret_anymore.txt
renamef -l
"""