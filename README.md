# renamef
A privacy oriented app that renames or summarizes documents using a local LLM.
(name pronounced in a Shakespearean manner with an English accent, followed by a snobbish twitch of an eyebrow)

## Features
add gif here

renamef's greatest strength is privacy: no data leaves your local machine and you can automate the renaming of as many files (theoretically) as you want.
One can use features like `listf` or `summf` to list files in a directory, or give you a summary of a given file. `renamef` is the meat of the app and allows one to rename all files in a directory (or its subdirectories) in an automated context-aware manner. And it _should_ work on Windows, Mac and Linux.

## Requirements
- Python
- Ollama (renamef will prompt for automated download & install)


renamef requires Python installed on your machine. Upon launch, it will check if you have Ollama installed, if not, it will attempt to install it and subsequentially pull the relevant model from Ollama to your machine. 
Python, Ollama, disk space, VRAM, supported OSs

## Installation
...

## Usage
How to start the app, then an example, and point to help

## Configuration

toml file: other ollama models, extending OCR language support

## Limitations
- renamef only supports the following file types: pdf, txt, md, png, jpeg, jpg, webp, gif
- By default, renamef uses a small 2 billion parameter local model (Gemma 4). Model accuracy varied in tests, but was still useful. Results improved with thinking mode on.
- Umlauts and Swedish characters in paths or file names are not currently supported.

## License
This project is licensed under the GNU AGPL-3.0 — see LICENSE.

It depends on PyMuPDF and pymupdf4llm by Artifex Software, licensed under AGPL-3.0.
Bundled Tesseract language data (tessdata/) is licensed under Apache 2.0 — see tessdata/LICENSE.
The LLM (Gemma 4) is downloaded via Ollama and is subject to its own license.
