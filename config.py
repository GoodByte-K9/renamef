import tomllib
from pathlib import Path

with open(Path(__file__).parent / "config.toml", "rb") as file:  # rb = read binary
    CONFIG = tomllib.load(file)
