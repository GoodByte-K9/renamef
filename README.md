# Renamef
A privacy oriented app that renames or summarizes documents using a local LLM.\
(name pronounced in a Shakespearean manner with an English accent, followed by a snobbish twitch of an eyebrow)

## Features
<img width="700" alt="renamef" src="https://github.com/user-attachments/assets/c653c182-e9c6-42ce-8cb2-87d92dff976c" />  
<br><br>

Renamef's greatest strength is privacy: no data leaves your local machine and you can automate the renaming of (theoretically) as many files as you want.
One can use features like `listf` or `summf` to list files in a directory or give you a summary of a given file. `renamef` is the meat of the app and allows one to rename all files in a directory (or its subdirectories) in an automated context-aware manner.

## Requirements
#### Recommended System specs
- **OS:** Linux, Windows or Mac
- **Memory:** 6GB VRAM (normal PC) or 16GB unified system memory (Mac)
- **Disk Space:** 10GB (PC) or 13GB (Mac) — Ollama installation + model takes majority of the space

#### Other
- Renamef requires Python installed on your machine.  
- Renamef will check if you have Ollama installed, if not, it will attempt to install it for you and subsequently pull the relevant model from Ollama to your machine.

## Installation
...

## Usage
1. Open terminal
2. Type `renamef` to launch the app
3. Type `help` for a list of commands
4. Type `<command> -h` for command-specific guidance and more examples

Example: `summf --thinking "C:\Users\Public\Documents\2026-03-14_product-spec_chronodyne.pdf"`\

<img width="700" alt="renamef_summf" src="https://github.com/user-attachments/assets/e7e09a39-0083-484d-9ffb-76aceff0d6d1" />

## Configuration
The following things can be configured in `renamef`:
- LLM used
- Supported languages (by default they are English, German and Finnish)
- Location of the tessdata folder

You can do any of the above by editing the `config.toml` file in the project's root with a text editor of your choice.

#### Changing the model
The underlying LLM can be changed simply by changing the model's name to one you wish to use. You can find a list of local models from the [Ollama website](https://ollama.com/search?c=local).  
Note, that larger models will require more VRAM or system memory than the default model.

#### Expanding language support
1. Download additional languages from [tesseract-ocr/tessdata](https://github.com/tesseract-ocr/tessdata)
2. Copy them to the **tessdata** folder in this project's root.
3. Add the additional language(s) to the `config.toml` file's "languages" variable under **\[ocr]**.

For example, to support Swedish you would download the **swe.traineddata** from Tesseract, add it to the `config.toml` file like so: `languages = "eng+deu+fin+swe"`, and you are good to go!

#### Changing tessdata folder path
In `config.toml` change the `tessdata = "default"` entry to an absolute path of your choice, e.g. `tessdata = "C:\Users\Public\Documents\tessdata"`

## Limitations
- Renamef only supports the following file types: pdf, txt, md, png, jpeg, jpg, webp, gif
- By default, Renamef uses a small 2 billion parameter local model (Gemma 4 e2b). Model accuracy varied in tests, but was still useful. Results improved with thinking mode on.
- Umlauts and Swedish characters in paths or file names are not currently supported. Note, that their presence inside documents is not an issue.
- By default, Renamef can read documents in three languages: English, German and Finnish. 

## License
This project is licensed under the GNU AGPL-3.0 — see LICENSE.

It depends on PyMuPDF and pymupdf4llm by Artifex Software, licensed under AGPL-3.0.
Bundled Tesseract language data (tessdata/) is licensed under Apache 2.0 — see tessdata/LICENSE.
The LLM (Gemma 4) is downloaded via Ollama and is subject to its own license.
