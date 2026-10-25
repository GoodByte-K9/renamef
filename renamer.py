from pathlib import Path

from tool_results import Result


def rename_files(rename_plan: list[dict[str, str]]) -> Result:
    # rename_plan example:
    # [{"original_path": "C:\\Users\\Public\\Public Documents\\12345678.PDF", "new_name": "deepest_secrets.pdf"}]
    file_data = Result()
    change_log = ["Successes: 0", "Failures: 0"]
    successes = 0
    failures = 0

    forbidden_characters = ["\\", "/", "..", ":", "*", "?", '"', "<", ">", "|"]
    for dictionary in rename_plan:
        full_path = dictionary["original_path"]
        new_name = dictionary["new_name"]
        # Check for sus in new_name
        if any(character in new_name for character in forbidden_characters):
            file_data.text = f"Error: Process interrupted. File name {new_name} contains illegal symbols or characters."
            return file_data

    # Execute the renaming plan
    for dictionary in rename_plan:
        full_path = dictionary["original_path"]
        new_name = dictionary["new_name"]
        original_path = Path(full_path)
        new_path = original_path.parent / new_name
        if original_path.is_file():
            try:
                original_path.rename(new_path)
            except OSError as e:
                error_message = str(e)
                failures += 1
                change_log.append(
                    f"OSError: {error_message}. Failed to rename {original_path.name} to {new_name}.")
            else:
                successes += 1
        else:
            change_log.append(f"Error: {full_path} is not a file...")
            failures += 1

    change_log[0] = f"Successes: {successes}"
    change_log[1] = f"Failures: {failures}"
    file_data.change_log = change_log
    print("Process finished.")
    return file_data


rename_files_function = {
    "name": "rename_files",
    "description": (
        "Rename one or more files. Each file keeps its folder; only the file name changes. "
        "Use this after deciding on new names for files the user has asked to rename. "
        "Returns a dataclass turned JSON with a change log listing each success and failure, "
        "with error details for failures."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "rename_plan": {
                "type": "array",
                "description": "The files to rename.",
                "items": {
                    "type": "object",
                    "properties": {
                        "original_path": {
                            "type": "string",
                            "description": "Absolute path of the existing file, including its file name.",
                        },
                        "new_name": {
                            "type": "string",
                            "description": "New file name only, including extension, without any folder path.",
                        },
                    },
                    "required": ["original_path", "new_name"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["rename_plan"],
        "additionalProperties": False,
    },
}

if __name__ == "__main__":
    rename_plan = [
        {
            "original_path": r"",
            "new_name": "shenanigansy.pdf",
        },
        {
            "original_path": r"",
            "new_name": "shenanigansy2.pdf",
        },
        {
            "original_path": r"",
            "new_name": "shenanigansy3.pdf",
        },
        {
            "original_path": r"",
            "new_name": "shenanigansy4.md",
        },
    ]
    print(rename_files(rename_plan))
