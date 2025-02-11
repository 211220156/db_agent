from abc import abstractmethod
from typing import Callable, Any
from .step_output import StepOutput

class Step:
    """
    基础执行步骤
    """
    judge_necessity: Callable[[Any], Any]
    name: str

    def __init__(self, judge_necessity = None):
        self.judge_necessity = judge_necessity

    @abstractmethod
    def exec(self, input: Any, **kwargs) -> StepOutput:
        """
        执行具体步骤的逻辑

        :param input: 输入
        :param kwargs: 包含相关上下文信息

        :return: 执行结果
        """
        raise NotImplementedError("execute method is not implemented.")