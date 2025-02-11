from typing import Any

from ..chain import Step
from ..step_output import StepOutput

class CallLLM(Step):

    name = 'CallLLM'

    def exec(self, input: Any, **kwargs) -> StepOutput:
        """
        调用LLM
        """
        context = kwargs.get("context")
        logger = kwargs.get("logger")

        # input是上一步生成的prompt
        response = context.config.model.chat(input, context, logger)
        if response is None:
            return StepOutput(
                output="",
                success=False,
                message="llm response None"
            )

        return StepOutput(
            output=response,
            message="Call llm success",
        )