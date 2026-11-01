import tempfile
import platform
import subprocess
from urllib.parse import urlparse
from pathlib import Path, PurePosixPath

from tqdm import tqdm
import requests
import psutil

from renamef import texts
from renamef.config import CONFIG

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

    if final_destination.is_file():
        return final_destination

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
    _os = platform.system()
    url = INSTALLER_URLS.get(_os)  # get() returns None if OS is not Windows or Mac
    if url is None:
        print("Automatic installation not supported for Linux. Run the following command to install Ollama:"
              f"\n{LINUX_COMMAND}")
        input("\nAfter installing Ollama, press Enter to continue...")
        return

    installer = download_installer(url)
    # launch installer:
    if _os == "Windows":
        print(texts.setup_wait)
        subprocess.run([str(installer)])
    elif _os == "Darwin":  # Darwin = Mac
        print(texts.setup_wait)
        subprocess.run(["open", str(installer)])


def is_process_running():
    for process in psutil.process_iter(["name"]):  # run through all active processes
        process_name = process.info["name"]
        if process_name is None:
            continue
        elif process_name.lower().startswith("ollama"):
            return True
    return False


def server() -> subprocess.Popen | None:
    if is_process_running():
        return None

    logs_folder = Path(__name__).parent / "logs"
    logs_folder.mkdir(parents=True, exist_ok=True)

    with open(logs_folder / "ollama.log", "a", encoding="utf-8") as log:  # "a" = append
        print("Starting up Ollama server...")
        ollama_server = subprocess.Popen(["ollama", "serve"], stdout=log, stderr=log)
    return ollama_server


def terminate_process(process):
    process.terminate()
    process.wait(timeout=5)
    if process:
        process.kill()


def pull_model() -> None:
    model = CONFIG["llm"]["model"]
    print(f"checking if {model} is available...")
    process_show = subprocess.run(["ollama", "show", model], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if process_show.returncode != 0:
        print(f"{model} not available. Initiating download...\n")
        process_pull = subprocess.run(["ollama", "pull", model])

        if process_pull.returncode != 0:
            print(f"Exit code {process_pull.returncode}")
            print("Failed to pull the model.\n"
                  "Check your internet connection, firewall rules and model name in config file\n"
                  "LLM features (summf, renamef with switches) are unavailable.")


if __name__ == "__main__":
    install()
