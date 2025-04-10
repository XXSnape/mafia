from dataclasses import dataclass


@dataclass
class ExtraCache:
    key: str
    need_to_clear: bool = True
    data_type: type = list
