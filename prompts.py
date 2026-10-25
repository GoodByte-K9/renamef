system_instruction = """You are an assistant who can list files, read them, and rename them; you have tools at your
disposal that enable you to do these in the user's file system. You are part of a file summarizing and renaming 
application. When a request starts with 'User requested', the message is static and sent by a function. Strictly follow
instructions and answer in concise and to the point manner. E.g. if you are asked to summarize a document, just give 
the summary with no preface or departing words."""

# !!! Prompts that originate from functions should always start with "User requested" !!! #
# ------------------------------------ SUMMF ------------------------------------ #
summf = """User requested a brief summary of the following document. Summarize it using your own words, answering the 
question 'what is this document for?'. Avoid disclosing names, social security numbers, phone numbers or personally 
identifiable information (PII). Avoid repetition in your description. Don't include questions in your answer. 
Document path: """
summf_default = " Use read_file() with the given absolute_file_path"
summf_expand = " Use read_file() with the given absolute_file_path and expand_context set to True."

# ------------------------------------ RENAMEF ------------------------------------ #
renamef_default = """User requested to rename one file based on its contents. Use the read_file tool to read the file 
and then rename the file with the rename_files tool based on the file's contents. If the file is linked to a company or 
institution, mention it in the file name, e.g. 'Microsoft_contract.pdf'. The file name can have a maximum of 
40 characters, file suffix included. Do NOT use the personal names of people in file names. Here's the file to be 
renamed: 
"""
