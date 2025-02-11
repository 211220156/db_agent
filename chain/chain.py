import logging

from .chain_context import ChainContext
from logger import Logger
from typing import List, Optional, Any
from exceptions import TypeError
from .step import Step
import time

class Chain:
    """
    执行链，每一个小步是step
    """
    _context: ChainContext
    _logger: Logger
    _steps: List[Step]

    def __init__(
        self,
        context: ChainContext,
        steps: Optional[List[Step]] = None,
        logger: Optional[Logger] = None,
    ):

        self._context = context
        self._steps = steps or []
        self._logger = logger or Logger(verbose=context.config.verbose, save_logs_to_file=context.config.save_logs)

    def run(self, input: Any = None) -> Any:
        """
        执行整条链路的逻辑，遍历每个step，执行其逻辑。输出进行统一的封装，便于数据传递.
        为了确保llm回答的稳定性，尝试n次调用。
        """
        max_request_time = self._context.config.max_request_time
        cur_request_time = 0

        cur_round_input = input
        # 执行n次Chain
        while cur_request_time < max_request_time:
            cur_request_time += 1

            try:
                for i, step in enumerate(self._steps):
                    self._logger.log(f"Chain round {cur_request_time}, running step {i + 1}: {step.name}")

                    if step.judge_necessity is not None and not step.judge_necessity(self._context):
                        self._logger.log(f"Chain round {cur_request_time}, step {i + 1} no necessity with context {self._context}")
                        continue

                    start_time = time.time()

                    # 执行逻辑
                    output = step.exec(
                        cur_round_input,
                        context=self._context,
                        logger=self._logger,
                    )

                    self._logger.log(f"Chain round {cur_request_time}, step {i + 1} output: {output}, executed in {time.time() - start_time:.2f} seconds")

                    if not output.success:
                        self._logger.log(f"Chain round {cur_request_time}, step {i + 1} failed. {output.message}")
                        # 重置输入为初始输入，重新运行
                        cur_round_input = input
                        break

                    if output.finish:
                        # 任务完成，返回输出
                        self._logger.log(f"Chain round {cur_request_time}, task finished at step {i + 1}, answer: {output.content}.")
                        return output.content

                    # 更新input
                    cur_round_input = output.content

                # 如果这一轮Chain所有操作执行成功，更新聊天记录
                self._update_chat_history()

            except Exception as e:
                self._logger.log(f"Chain round {cur_request_time}, error when running step {i + 1} : {e}", logging.ERROR)
                raise e

        self._logger.log(f"Chain run failed after {max_request_time} retry.", logging.ERROR)
        return "Sorry, due to some error, I can't answer your question at the moment, please try again later."

    def _update_chat_history(self):
        """
        当一次调用链成功结束后，需要更新消息到
        """
        if user_prompt := self._context.get("user_prompt"):
            self._context.append_history(role="user", content=user_prompt)

        if assistant_msg := self._context.get("assistant_msg"):
            self._context.append_history(role="assistant", content=assistant_msg)

        if execution_result := self._context.get("execution_result"):
            self._context.append_history(role="user", content=execution_result)


    def append(self, step: Step):
        if not isinstance(step, Step):
            raise TypeError(
                f"Only Step can be appended to Chain, got {type(step)}."
            )
        self._steps.append(step)

    def __or__(self, chain: 'Chain') -> 'Chain':
        """
        拼接两个Chain
        """

        if not isinstance(chain, Chain):
            raise TypeError(
                f"Only Chain can be concatenated with Chain, however {type(chain)} are provided."
            )

        new_chain = Chain(
            context=self._context,
            logger=self._logger,
            steps=self._steps
        )

        for step in chain._steps:
            new_chain.append(step)

        return new_chain