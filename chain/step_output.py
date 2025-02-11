from typing import Any, Optional

class StepOutput:
    """
    Step的输出
    """

    content: Any
    message: str
    success: bool
    finish: bool # 标志是否结束该Chain
    attachment: dict

    def __init__(self,
        output: Any = None,
        message: Optional[str] = None,
        success: bool = True,
        finish: bool = False,
        attachment: Optional[dict] = None
    ) -> None:
        self.content = output
        self.message = message
        self.success = success
        self.finish = finish
        self.attachment = attachment

    def __str__(self) -> str:
        obj = {
            "content": self.content,
            "message": self.message,
            "success": self.success,
            "finish": self.finish,
            "attachment": self.attachment
        }

        return obj.__str__()