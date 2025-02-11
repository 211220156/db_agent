import logging
import os, json
from typing import List, Optional
from .model import Model
# from chain import ChainContext
# from chain import Message as Msg
from logger import Logger

import dashscope
from dashscope.api_entities.dashscope_response import Message

from helpers import load_env

load_env()

class DashScope(Model):

    model_type = "DashScope"

    few_shot_cot_history = [
        Message(role="user", content="Roger has 5 tennis balls. He buys 2 more cans of tennis balls. Each can has 3 tennis balls. How many tennis balls does he have now?"),
        Message(role="assistant", content="Roger started with 5 balls. 2 cans of 3 tennis balls each is 6 tennis balls. 5 + 6 = 11. The answer is 11."),
        Message(role="user", content="How many keystrokes are needed to type the numbers from 1 to 500? Answer Choices: (a) 1156 (b) 1392 (c) 1480 (d) 1562 (e) 1788"),
        Message(role="assistant", content="There are 9 one-digit numbers from 1 to 9. There are 90 two-digit numbers from 10 to 99. There are 401 three-digit numbers from 100 to 500. 9 + 90(2) + 401(3) = 1392. The answer is (b).")
    ]

    def __init__(self):
        self.api_key = os.environ.get('DASH_SCOPE_API_KEY')
        self.model_name = os.environ.get('MODEL_NAME')
        self._client = dashscope.Generation()
        self.max_retry_time = 5

    def _convert_message(self, messages) -> List[Message]:
        """
        将通用的Message转换成dashscope的消息格式
        """
        result = []
        for message in messages:
            result.append(Message(role=message.role, content=message.content))

        return result

    def chat(self, prompt: str, context = None, logger: Logger = None) -> Optional[str]:
        """
        需要从context中提取出history
        """
        # 将通用的chain.Message转换为特定的大模型的Message格式
        messages = self.few_shot_cot_history + self._convert_message(context.history)
        messages.append(Message(role="user", content=prompt))

        cur_retry_time = 0
        while cur_retry_time < self.max_retry_time:
            cur_retry_time += 1
            try:

                response = self._client.call(
                    model=self.model_name,
                    api_key=self.api_key,
                    messages=messages
                )

                logger.log("response:{}".format(response))

                # content = json.loads(response["output"]["text"])

                # 无异常发生，正常调用得到结果后，再添加当前prompt进入history
                # context.append_history(role="user", content=prompt)

                # 更新user prompt，用于更新聊天历史
                context.add("user_prompt", prompt)

                # return content
                return response["output"]["text"]
            except Exception as e:
                logger.log("call DashScope llm exception:{}".format(e))

        logger.log(f"call DashScope error, prompt:{prompt}", logging.ERROR)
        return None