from pathlib import Path
from typing import cast
import base64
import os

import pymupdf4llm
import pymupdf

from tool_results import Result
from config import CONFIG

if CONFIG["ocr"]["tessdata"] not in ["tessdata", "default"]:
    os.environ["TESSDATA_PREFIX"] = CONFIG["ocr"]["tessdata"]
else:
    os.environ["TESSDATA_PREFIX"] = str(Path(__file__).parent / "tessdata")
ocr_languages = CONFIG["ocr"]["languages"]


# ------------------------------ LIST FILES ------------------------------ #
def list_files(folder_path: str, recursive_listing: bool = False) -> Result:
    def find_folders_recursively(absolute_path: Path) -> list[Path]:
        recursive_directories = [directory for directory in absolute_path.rglob("*/")]
        recursive_directories.insert(0, absolute_path)
        return recursive_directories

    def add_files_to_documents(absolute_path: Path) -> None:
        for f in absolute_path.iterdir():  # f = file or folder. Looping through all of them
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
        recursive_folders: list = find_folders_recursively(root_path) if recursive_listing is True else []
        if recursive_folders:
            for folder in recursive_folders:
                add_files_to_documents(folder)
        else:
            add_files_to_documents(root_path)
    elif root_path.is_file():
        file_data.text = "ERROR: Path is not a directory"
        return file_data
    if any(documents_paths.values()):
        file_data.paths = documents_paths
    else:
        file_data.text = "WARNING: No files supported by this tool were found."
    return file_data


list_files_function = {
    "name": "list_files",
    "description": "Read a file in a given folder path. The function returns a dataclass turned JSON. If something "
                   "goes wrong, it returns a list[str] with a 'WARNING:' or 'ERROR:' message. The function will only "
                   "check for the following files: pdf, txt, md, png, jpeg, jpg, webp, gif.",
    "parameters": {
        "type": "object",
        "properties": {
            "folder_path": {
                "type": "string",
                "description": "The full absolute path where file(s) reside. If the path ends with a file name, only"
                               "that one file is read."
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
    char_limit = 1500 if expand_context is False else 2500

    if file_path.is_file():
        file_suffix = file_path.suffix.lower()
        if file_suffix == ".pdf":
            file_data.text = cast(
                str, pymupdf4llm.to_markdown(file_path, ocr_language=CONFIG["ocr"]["languages"])[:char_limit])
            if file_data.text == "":
                doc = pymupdf.open(file_path)
                pages = 1 if expand_context is False else len(doc)
                for page_num in range(pages):
                    image_bytes = doc[page_num].get_pixmap().tobytes(output="png")  # Transform page image to binary
                    encode_image(data_object=file_data, img_bytes=image_bytes, suffix="png")
        elif file_suffix == ".txt" or file_suffix == ".md":
            file_data.text = file_path.read_text(encoding="utf-8")[:char_limit]
        elif file_suffix in [".png", ".jpeg", ".jpg", ".webp", ".gif"]:
            suffix_clean = file_suffix.strip(".")  # Returns "png" or "jpeg" etc.
            image_bytes = file_path.read_bytes()
            encode_image(data_object=file_data, img_bytes=image_bytes, suffix=suffix_clean)
        else:
            file_data.text = "ERROR: File type is not supported and cannot be read..."
    elif file_path.is_dir():
        file_data.text = "ERROR: Received file path was a directory, not a file..."
    else:
        file_data.text = "ERROR: Incorrect path — path, filename, or suffix might be erroneous..."

    return file_data


read_file_function = {
    "name": "read_file",
    "description": "Read a file in a given folder path. If it's a scanned pdf, it will use OCR to retrieve text."
                   "If it fails to do so, it will send the image of the pdf for you to parse. Other images are also "
                   "processed and sent to you in data url format. By default the function will return a maximum of "
                   "1500 characters of text, or 1 image. The function returns a dataclass turned JSON. If something "
                   "goes wrong, it returns a list[str] with a 'WARNING:' or 'ERROR:' message.",
    "parameters": {
        "type": "object",
        "properties": {
            "folder_path": {
                "type": "string",
                "description": "The full absolute path where pdf(s) reside. If the path ends with a file name, only"
                               "that one file is read."
            },
            "expand_context": {
                "type": "boolean",
                "description": "If True, function will return up to 1500 characters of text, or send all images in a "
                               "pdf. Use only when you lack enough context to understand the document."
            }
        },
        "required": ["folder_path"],
        "additionalProperties": False
    }
}

if __name__ == "__main__":
    print(read_file(r""))
