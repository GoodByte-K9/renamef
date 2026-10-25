from dataclasses import dataclass, field


@dataclass
class Result:
    text: str = ""
    change_log: list = field(default_factory=list)
    image: list = field(default_factory=list)
    paths: dict[str, list] = field(default_factory=dict)


@dataclass()
class FileNameSuggestions:
    listf_list: dict[str, list]
    rename_plan: list[dict[str, str]]
