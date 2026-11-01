import sys
import shlex
import shutil
import platform

from openai import APIConnectionError

from renamef.commands import parse_arguments
from renamef import ollama_manager
from renamef import texts


def run() -> None:
    app_response = ""

    print("checking if Ollama is installed...")
    if shutil.which("ollama") is None:
        while True:
            install_confirmation = input(texts.install_confirmation).strip().lower()
            if install_confirmation in ["yes", "y"]:
                ollama_manager.install()
                break
            elif install_confirmation in ["no", "n"]:
                print(f"\n{texts.install_warning}\n")
                sys.exit()
            else:
                print("Invalid answer...")

    if shutil.which("ollama") is None:
        print("No Ollama installation detected. Exiting...\n")
        sys.exit()

    print("checking if ollama server is running...")
    ollama_server = ollama_manager.server()
    ollama_manager.pull_model()
    print(f"{texts.art}\n{texts.welcome}")

    # Must specify POSIX for shlex, lest it fail at reading paths with backslashes
    is_posix = False if platform.system() == "Windows" else True
    try:
        while True:
            try:
                user_input = shlex.split(input("\n> "), posix=is_posix)
                print("")
            except ValueError as e:
                print(f"{e}. Please try again...")
                continue
            try:
                app_response = parse_arguments(user_input)
            except SystemExit:
                pass
            except APIConnectionError:
                print("\nError: failed to reach LLM...")
                ollama_server = ollama_manager.server()
                if ollama_server is None:
                    sys.exit("Failed to restart Ollama server, exiting app...")
            if app_response == "exit":
                print("\nExiting...\n")
                break
    except KeyboardInterrupt:
        print()
        sys.exit()
    finally:
        if ollama_server is not None:
            ollama_manager.terminate_process(ollama_server)


if __name__ == "__main__":
    run()
