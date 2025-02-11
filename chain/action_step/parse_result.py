import json, re
import logging
from typing import Any, Optional

from prompt import df_expected_format
from .. import ChainContext
from ..chain import Step
from ..step_output import StepOutput
from logger import Logger


class ParseResult(Step):
    """
    结果解析。尝试将llm的结果解析为dict形式，并提取出相关信息。

    若解析得出任务已完成，返回finish为True的答案
    """
    name = "ParseResult"
    context: ChainContext
    logger: Logger

    def _validate(self, obj, format_spec):
        """递归验证字典的结构和类型"""
        if not isinstance(obj, dict) or not isinstance(format_spec, dict):
            return False

        for key, expected_type in format_spec.items():
            if key not in obj:
                return False

            value = obj[key]
            if isinstance(expected_type, type):
                # 检查类型
                if not isinstance(value, expected_type):
                    return False
            elif isinstance(expected_type, dict) and len(expected_type) == 1:
                # 检查动态键值类型 {key_type: value_type}
                key_type, value_type = list(expected_type.items())[0]
                if not isinstance(value, dict):
                    return False
                for sub_key, sub_value in value.items():
                    # 只验证键和值的类型，不强制验证键的具体内容
                    if not isinstance(sub_key, key_type) or not isinstance(sub_value, value_type):
                        return False
            elif isinstance(expected_type, dict):
                # 递归验证嵌套字典
                if not self._validate(value, expected_type):
                    return False
            else:
                # 无效的格式规范
                return False

        return True

    def _extract_thoughts(self, response):
        try:
            thoughts = response.get("thoughts")
            observation = response.get("observation")
            plan = thoughts.get("plan")
            criticism = thoughts.get("criticism")
            speak = thoughts.get("speak")
            reasoning = thoughts.get("reasoning")

            assistant_msg = f"plan: {plan}\ncriticism: {criticism}\nspeak: {speak}\nreasoning: {reasoning}\nobservation: {observation}"
            # 将assistant_msg写入context.history
            # self.context.append_history(role="assistant", content=assistant_msg)

            self.context.add("assistant_msg", assistant_msg)
            self.logger.log(f"Extract thoughts: {assistant_msg}")

        except Exception as e:
            self.logger.log("Extract thoughts exception:{}".format(e))

    def _escape_newlines_in_quotes(self, input_str: str) -> str:
        """
        在类json字符串中，转义双引号字符串中未转义的换行符。
        用于编码llm回复中代码部分的换行符，避免影响后续json.loads。

        Args:
            input_str (str)：包含JSON数据的输入字符串

        Returns:
            str：经过处理的JSON字符串，双引号内的换行符被转义。
        """
        # Regular expression to find text inside double quotes
        pattern = r'(".*?")'

        def replace_newlines(match):
            text = match.group(1)
            if '"' in text:
                # Only replace direct newlines (not already escaped ones)
                text = text.replace("\n", "\\n")
            return text

        # Apply the replacement only to the content inside quotes
        return re.sub(pattern, replace_newlines, input_str, flags=re.DOTALL)

    def _preprocess_code(self, raw_code: str) -> str:
        """
        处理原始代码字符串，将其转换为可用 exec 执行的 Python 代码。

        Args:
            raw_code (str): 原始代码字符串。

        Returns:
            str: 处理后的可执行代码。
        """
        # 去掉代码块标记和首尾多余的换行符
        lines = raw_code.strip().splitlines()
        clean_lines = [line for line in lines if not line.strip().startswith("```")]

        # 合并成一个字符串
        executable_code = "\n".join(clean_lines)
        return executable_code

    def exec(self, input: Any, **kwargs) -> StepOutput:
        self.context = kwargs.get("context")
        self.logger = kwargs.get("logger")

        try:
            self.logger.log(f"input:{input}")
            input = self._escape_newlines_in_quotes(input)
            self.logger.log(f"fix(input):{input}")
            response = json.loads(input)

            # 验证是否符合格式要求
            if not self._validate(response, df_expected_format):
                self.logger.log(f"The format requirements are not met with response: {response} ")
                return StepOutput(
                    success=False,
                    message="Bad response format"
                )

            # 符合要求，开始解析各部分。将相关思考内容写入context.history，作为assistant message
            self._extract_thoughts(response)

            # 判断是否finish，是的话StepOutput设置为True，返回答案；否则将生成的代码返回
            code = response.get("code")
            finish = response.get("finish")
            answer = response.get("answer")
            if finish == 'True':
                self.logger.log(f"Task finish, answer:{answer}")
                return StepOutput(
                    success=True,
                    finish=True,
                    output=answer
                )

            # 把code提取成正确格式
            code = self._preprocess_code(code)
            self.logger.log(f"processed_code:{code}")


            return StepOutput(
                success=True,
                # TODO 删掉，只用于测试
                # finish=True,
                output=code
            )

        except Exception as e:
            self.logger.log(f"Parse result exception: {e}, input: {input}", logging.ERROR)
            return StepOutput(
                success=False,
                message=f"Parse result exception: {e}"
            )
