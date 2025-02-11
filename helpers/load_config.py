import json
from typing import Optional
from helpers import concat_path
from config import Config
from model import DashScope

def load_from_json(initial_values: Optional[dict] = None) -> Config:
    """
    从json中加载，创建一个Config对象
    """
    config = {}

    try:
        with open(concat_path("config.json"), "r") as f:
            config = json.load(f)

    except FileNotFoundError:
        pass

    if initial_values is not None:
        config.update(initial_values)

    if config.get("model") is None:
        config["model"] = DashScope()

    return Config(**config)