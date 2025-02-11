# import json
from pydantic import BaseModel
# from typing import Optional
# from helpers import concat_path
from model import Model

class Config(BaseModel):
    verbose: bool = False
    max_request_time: int = 10
    model: Model = None
    save_logs_to_file: bool = True

    class Config:
        arbitrary_types_allowed = True

    # @classmethod
    # def load_from_json(cls, initial_values: Optional[dict] = None) -> Config:
    #     """
    #     从json中加载，创建一个Config对象
    #     """
    #     config = {}
    #
    #     try:
    #         with open(concat_path("config.json"), "r") as f:
    #             config = json.load(f)
    #
    #     except FileNotFoundError:
    #         pass
    #
    #     if initial_values is not None:
    #         config.update(initial_values)
    #
    #     if config.get("model") is None:
    #         config["model"] = DashScope()
    #
    #     return Config(**config)