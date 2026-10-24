from pathlib import Path, PurePosixPath
from urllib.parse import urlparse
import subprocess
import platform
import tempfile
import psutil

import requests
from tqdm import tqdm

from config import CONFIG

INSTALLER_URLS = {
            "Windows": "https://ollama.com/download/OllamaSetup.exe",
            "Darwin": "https://ollama.com/download/Ollama.dmg"  # Darwin = Mac
        }
LINUX_COMMAND = "curl -fsSL https://ollama.com/install.sh | sh"


def download_installer(url: str) -> Path | None:
    # Extract file name from download link; get temp folder path; combine them for final download destination:
    url_components = urlparse(url)
    # ParseResult(scheme='https', netloc='ollama.com', path='/download/OllamaSetup.exe',
    #             params='', query='', fragment='')
    url_path = url_components.path  # '/download/OllamaSetup.exe'
    installer_name = PurePosixPath(url_path).name  # turn into path object and keep name only: 'OllamaSetup.exe'
    final_destination = Path(tempfile.gettempdir()) / installer_name  # C:\ ... \Temp\OllamaSetup.exe 💀

    # stream=True prevents loading the entire response into memory at once, downloading it one chunk at a time:
    with requests.get(url, stream=True, timeout=30) as response:
        response.raise_for_status()
        installer_size = int(response.headers.get("content-length", 0))  # response body size in bytes; default: 0

        with open(final_destination, "wb") as file:  # wb = write binary in final_destination
            with tqdm(total=installer_size, unit="B", unit_scale=True, desc="Downloading") as bar:
                # iter_content() reads chunks produced by requests.get(stream=True); only 1 chunk is in memory at a time
                for chunk in response.iter_content(chunk_size=1024*1024):  # chunk: a 1024*1024 bytes sized chunk (1MB)
                    file.write(chunk)
                    bar.update(len(chunk))
    return final_destination


def install() -> None:
    url = INSTALLER_URLS.get(platform.system())  # get() returns None if retrieved OS name not in dict
    _os = platform.system()
    if url is None:
        print("Automatic installation not supported on Linux. Run the following command to install Ollama:"
              f"\n{LINUX_COMMAND}")
        return

    installer = download_installer(url)
    # launch installer:
    if _os == "Windows":
        subprocess.Popen([str(installer)])
    elif _os == "Darwin":  # Darwin = Mac
        subprocess.run(["open", str(installer)])


def server() -> None:
    for process in psutil.process_iter(["name"]):  # run through all active processes
        process_name = process.info["name"]
        if process_name is None:
            continue
        elif process_name.lower().startswith("ollama"):
            return None

    logs_folder = Path(__name__).parent / "logs"
    logs_folder.mkdir(parents=True, exist_ok=True)

    with open("logs/ollama.log", "a", encoding="utf-8") as log:  # "a" = append
        subprocess.Popen(["ollama", "serve"], stdout=log, stderr=log)
    return None


def pull_model() -> None:
    model = CONFIG["llm"]["model"]
    process_show = subprocess.run(["ollama", "show", model], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if process_show.returncode != 0:
        process_pull = subprocess.run(["ollama", "pull", model])

        if process_pull.returncode != 0:
            print(f"Exit code {process_pull.returncode}")
            print("Failed to pull the model.\n"
                  "Check your internet connection, firewall rules and model name in config file\n"
                  "LLM features (summf, renamef with switches) are unavailable.")


if __name__ == "__main__":
    install()
