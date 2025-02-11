import inspect
from typing import Any, Callable, List, Optional

class AgentFunction:
    """
    封装Agent可使用的函数
    """
    func: Callable[..., Any]
    desc: str
    name: str

    def __init__(
        self,
        func: Callable[..., Any],
        desc: Optional[str] = None,
    ):
        self.func = func
        self.name = func.__name__

        func_desc = desc or func.__doc__

        self.desc = f"""<function>
def {self.name}{inspect.signature(self.func)}:                            
    \"\"\"{func_desc}\"\"\"
</function>"""

    def __call__(self, *args, **kwargs) -> Any:
        """
        调用函数
        """
        return self.func(*args, **kwargs)

    def __str__(self) -> str:
        return self.desc


def is_tool_existed(tool_name: str, tools: List[AgentFunction]) -> bool:
    return any(tool.name == tool_name for tool in tools)

def get_func_by_name(tool_name: str, tools: List[AgentFunction]) -> Callable[..., Any]:
    return next((tool for tool in tools if tool.name == tool_name), None)

def to_string(tools: List[AgentFunction]) -> str:
    return "\n".join(str(tool) for tool in tools)

