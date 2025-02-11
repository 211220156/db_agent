from abc import abstractmethod
from typing import Optional, TYPE_CHECKING

from exceptions import NotImplementedError
from logger import Logger

if TYPE_CHECKING:
    from chain.chain_context import ChainContext # 避免循环导入

class Model:

    model_type: str
    model_name: str

    @abstractmethod
    def chat(self, prompt: str, context: 'ChainContext' = None, logger: Logger = None) -> Optional[str]:
        """
        向大语言模型提问
        """
        raise NotImplementedError("No Chat Method")