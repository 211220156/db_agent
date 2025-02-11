from typing import List, Optional, Any
import pandas as pd
from config import Config
from helpers.load_config import load_from_json
from .message import Message
from helpers.agent_function import AgentFunction, to_string

class ChainContext:
    """
    执行链的上下文信息，包含所需要的变量
    """
    dfs: List[pd.DataFrame]
    config: Config
    history: List[Message]
    values: dict
    tools: List[AgentFunction]


    def __init__(
        self,
        dfs: List[pd.DataFrame],
        tools: Optional[List[AgentFunction]] = None,
        config: Optional[Config] = None,
        history: Optional[List[Message]] = None,
        values: Optional[dict] = None,
    ):
        self.dfs = dfs
        self.tools = tools or []

        self.config = config or load_from_json()

        self.history = history or []

        self.values = values or {}

    def add(self, key: str, value: Any):
        self.values[key] = value

    def add_many(self, values: dict):
        self.values.update(values)

    def get(self, key: str, default: Any = None):
        return self.values.get(key, default)

    def clear_history(self):
        self.history = []

    def append_history(self, role: str, content: str):
        self.history.append(Message(role=role, content=content))

    def get_tools_desc(self) -> str:
        return to_string(self.tools)


