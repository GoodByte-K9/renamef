system_instruction = """You are an assistant who can list files, read them, and rename them; you have tools at your
disposal that enable you to do these in the user's file system. You are part of a file summarizing and renaming 
application. When a request starts with 'User requested', the message is static and sent by a function. Strictly follow
instructions and answer in concise and to the point manner. E.g. if you are asked to summarize a document, just give 
the summary with no preface or departing words."""

# !!! Prompts that originate from functions should always start with "User requested" !!! #
""
summf = """User requested a brief summary of the following document. Summarize it using your own words, answering the 
question 'what is this document for?'. Avoid disclosing names, social security numbers, phone numbers or personally 
identifiable information (PII). Avoid repetition in your description. Document path: """
summf_default = " Use read_file() with the given absolute_file_path"
summf_expand = " Use read_file() with the given absolute_file_path and expand_context set to True."
