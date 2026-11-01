import os
import sys
import base64
import logging
import contextlib
from typing import cast
from pathlib import Path

import pymupdf4llm
import pymupdf

from renamef.config import CONFIG
from renamef.tool_results import Result

if CONFIG["ocr"]["tessdata"] not in ["tessdata", "default"]:
    os.environ["TESSDATA_PREFIX"] = CONFIG["ocr"]["tessdata"]
else:
    os.environ["TESSDATA_PREFIX"] = str(Path(__file__).parent / "tessdata")
ocr_languages = CONFIG["ocr"]["languages"]


# disabling pesky OCR warnings:
pymupdf.set_messages(pylogging=True)  # sends messages to Python logging system instead of writing to the terminal
# get the pymupdf logger and set its logging level to ERROR, so it only displays ERROR and CRITICAL messages
logging.getLogger("pymupdf").setLevel(logging.ERROR)


# ------------------------------ BLOW OCR STDERR TO OBLIVION ------------------------------ #
# The below decorator, together with the 'with' keyword, enables the function to be run in two parts. 'yield' splits...
@contextlib.contextmanager  # ...the function effectively in two, with the latter part running when 'with' closes...
def silence_native_stderr():  # ...This is possible because 'yield' turns the function into a generator.
    sys.stderr.flush()  # Force all error messages out of Python's buffer
    # Save where stderr (file descriptor/fd 2) points to, so the right target can be restored later.
    saved_stderr = os.dup(2)  # The stderr target will be stored in another number, chosen by the OS
    # Store an open connection in 'devnull' in the form of a descriptor number, chosen by the OS.
    devnull = os.open(os.devnull, os.O_WRONLY)  # O_WONLY allows write-only when using the 'devnull' variable
    # try/finally ensures fd 2 is pointed back to its original target even if OCR crashes, so they are not strictly...
    try:  # ...necessary for the function's "split logic" to work.
        # Change the target where fd 2 points to devnull: an empty all-consuming void
        os.dup2(devnull, 2)  # dup() cannot specify any file descriptors to manipulate, but dup2() can.
        yield
    finally:
        sys.stderr.flush()
        os.dup2(saved_stderr, 2)  # Restore the original target for fd 2
        os.close(devnull)
        os.close(saved_stderr)


# ------------------------------ LIST FILES ------------------------------ #
def list_files(folder_path: str, recursive_listing: bool = False) -> Result:
    def find_folders_recursively(absolute_path: Path) -> list[Path] | Result:
        recursive_directories = [directory for directory in absolute_path.rglob("*/")]
        if recursive_directories:
            recursive_directories.insert(0, absolute_path)
        return recursive_directories

    def add_files_to_documents(absolute_path: Path) -> None:
        try:
            paths_list = list(absolute_path.iterdir())
        except PermissionError as e:
            file_data.text = f"ERROR: {e}"
        else:
            for f in paths_list:  # f = file or folder. Looping through all of them
                if f.is_file():
                    for key in documents_paths.keys():
                        if f.suffix.lower() == key:
                            documents_paths[key].append(str(f))

    file_data = Result()
    documents_paths: dict = {  # Filled up by the add_files_to_documents() function
        ".pdf": [],
        ".txt": [],
        ".md": [],
        ".png": [],
        ".jpeg": [],
        ".jpg": [],
        ".webp": [],
        ".gif": [],
    }
    root_path = Path(folder_path)  # Convert folder_path into a Path object
    if root_path.is_dir():
        recursive_folders: list | Result = find_folders_recursively(root_path) if recursive_listing else []
        if isinstance(recursive_folders, list) and recursive_folders:
            for folder in recursive_folders:
                add_files_to_documents(folder)
        elif isinstance(recursive_folders, list) and not recursive_folders:
            add_files_to_documents(root_path)
        elif isinstance(recursive_folders, Result):
            file_data = recursive_folders
            return file_data
        if file_data.text:
            return file_data

    elif root_path.is_file():
        file_data.text = "ERROR: Path is not a directory..."
        return file_data
    elif not root_path.is_file() and not root_path.is_dir():
        file_data.text = "ERROR: Path does not exist..."
        return file_data
    if any(documents_paths.values()):
        file_data.paths = documents_paths
    else:
        file_data.text = "WARNING: No supported files in given path..."
    return file_data


list_files_function = {
    "name": "list_files",
    "description": "List all files in a given folder path. The function returns a dataclass turned JSON. If something "
                   "goes wrong, it shows a relevant 'WARNING:' or 'ERROR:' message. The function will only "
                   "check for the following files: pdf, txt, md, png, jpeg, jpg, webp, gif.",
    "parameters": {
        "type": "object",
        "properties": {
            "folder_path": {
                "type": "string",
                "description": "The full absolute path where file(s) reside."
            },
            "recursive_listing": {
                "type": "boolean",
                "description": "If True, the tool scans all folders recursively in the target path for files."
            }
        },
        "required": ["folder_path"],
        "additionalProperties": False
    }
}


# ------------------------------ READ A FILE ------------------------------ #
def read_file(absolute_file_path: str, expand_context: bool = False) -> Result:
    def encode_image(data_object: Result, img_bytes: bytes, suffix: str) -> None:
        image_base64 = base64.b64encode(img_bytes).decode("utf-8")  # Encode to Base64
        media_type = f"image/{suffix}" if suffix != "jpg" else f"image/jpeg"
        data_object.image.append(image_base64)
        data_object.text = media_type

    file_data = Result()
    file_path = Path(absolute_file_path)
    char_limit = 1500 if not expand_context else 2500

    if file_path.is_file():
        file_suffix = file_path.suffix.lower()

        if file_suffix == ".pdf":
            try:
                doc = pymupdf.open(file_path)
            except pymupdf.FileDataError:
                file_data.text = "ERROR: Document is broken or corrupted..."
                return file_data
            else:
                if doc.needs_pass:
                    file_data.text = "ERROR: Document is password protected and cannot be read..."
                    doc.close()
                    return file_data

            pages_2_read: int = len(doc) if len(doc) <= 3 else 3
            with silence_native_stderr():
                file_data.text = cast(
                    str, pymupdf4llm.to_markdown(
                        file_path,
                        pages=[0] if not expand_context else [nr for nr in range(pages_2_read)],
                        ocr_language=ocr_languages
                    )[:char_limit])
            if file_data.text.strip() == "":
                for page_num in range(1 if not expand_context else pages_2_read):
                    image_bytes = doc[page_num].get_pixmap(dpi=200).tobytes(output="png")  # Transform to binary
                    encode_image(data_object=file_data, img_bytes=image_bytes, suffix="png")
            doc.close()
        elif file_suffix == ".txt" or file_suffix == ".md":
            file_data.text = file_path.read_text(encoding="utf-8", errors="replace")[:char_limit]

        elif file_suffix in [".png", ".jpeg", ".jpg", ".webp", ".gif"]:
            suffix_clean = file_suffix.strip(".")  # Returns "png" or "jpeg" etc.
            image_bytes = file_path.read_bytes()
            encode_image(data_object=file_data, img_bytes=image_bytes, suffix=suffix_clean)

        else:
            file_data.text = "ERROR: File type is not supported and cannot be read..."

    elif file_path.is_dir():
        file_data.text = "ERROR: Received file path was a directory, not a file..."
    else:
        file_data.text = "ERROR: Incorrect path. Path, filename, or suffix might be erroneous, or access was denied..."

    return file_data


read_file_function = {
    "name": "read_file",
    "description": "Read a file in a given folder path. If it's a scanned pdf, it will use OCR to retrieve text. "
                   "If it fails to do so, it will send the image of the pdf for you to parse. Other images are also "
                   "processed and sent to you in data url format. By default the function will return a maximum of "
                   "1500 characters of text, or 1 image. The function returns a dataclass turned JSON. If something "
                   "goes wrong, it returns a Result object representation with an 'ERROR:' message.",
    "parameters": {
        "type": "object",
        "properties": {
            "absolute_file_path": {
                "type": "string",
                "description": "The full absolute path where a file resides."
            },
            "expand_context": {
                "type": "boolean",
                "description": "If True, function will return up to 2500 characters of text, or send up to 3 images "
                               "from a pdf. Use only when you lack enough context to understand the document."
            }
        },
        "required": ["absolute_file_path"],
        "additionalProperties": False
    }
}

if __name__ == "__main__":
    print(list_files(r"C:\Users\Public\Documents"))
