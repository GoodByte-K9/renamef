system_instruction = """You are an assistant who can list files, read them, and rename them; you have tools at your
disposal that enable you to do these in the user's file system. You are part of a file summarizing and renaming 
application. When a request starts with "User requested", the message is static and sent by a function. Strictly follow
instructions and answer in concise and to the point manner. E.g. if you are asked to summarize a document, just give 
the summary with no preface or departing words."""

# !!! Prompts that originate from functions should always start with "User requested" !!! #
# ------------------------------------ SUMMF ------------------------------------ #
summf = """User requested a brief summary of the following document. 

Summarization Rules:
- Only state what the document actually says
- The summary should be able to answer the questions "what is this document about?" and "whom is it from?"
- Avoid disclosing personal names or other personally identifiable information
- Avoid repetition in your description
- If the sender is not knows, speak of them as "unknown"

Answer Format
- Use the following two titles: "What is this document about?" and "Whom is it from?"
- Write a concise summary, using 1-3 sentences, under both titles following title themes

Example 1:
What is this document about?
This document is an electric bill.

Whom is it from?
It was sent by EDF Energy.

Example 2:
What is this document about?
This document is an employment contract for a software developer position. It covers salary, working hours, 
and a six-month probation period.

Who is it from?
It is from Acme Corp.

Example 3:
What is this document about?
This document is a short meeting note listing three action items for an upcoming office move.

Who is it from?
Unknown.

Document to summarize: """
summf_default = """
Use read_file() with the given absolute_file_path"""
summf_expand = """
Use read_file() with the given absolute_file_path and expand_context set to True."""

# ------------------------------------ RENAMEF ------------------------------------ #
renamef_default = """User requested to rename one file based on its contents. 
1. Use read_file() tool to read the file 
2. Rename the file with rename_files() based on its contents

File Naming Rules:
- Mention relevant company or institution in the name if present
- If the document has a date written in it, include it
- Don't include file path in the name
- Don't include personal names or personally identifiable information
- Naming convention: 'YYYY-MM-DD_document-type_organization.suffix', all lowercase, hyphens within a part, 
underscores between parts. Use YYYY-MM or YYYY when full date is not available.
- Keep original file extension in the name
- Don't use generic descriptive terms like 'document'
- Maximum 40 characters long file names.

Examples:
- '2025-08-15_lease_baker-street-221b.pdf'
- '2026-09-30_payslip_acme-corp.pdf'
- '2026-10-05_invoice_vodafone.pdf'
- '2026-09_bank-statement_hsbc.pdf'
- '2025_tax-return.pdf'
- '2026-02-10_power-of-attorney.pdf'
- '2025-11-20_warranty_samsung-tv.pdf'

Response structure:
- 'Old name: <old_name> | New name: <new_name>...', and nothing else.

Examples:
- 'Old name: 123456.txt | New name: 1984-06-01_notes_ministry-of-truth.txt...'
- 'Old name: IMG_20260114.jpg | New name: 2026-01-14_parking-fine_city-council.jpg...'
- 'Old name: scan_0042.pdf | New name: 2025-12_electricity-bill_edf.pdf...'
- 'Old name: download (3).pdf | New name: 2026-06-03_car-insurance_allianz.pdf...'

Here's the file to be renamed: """
