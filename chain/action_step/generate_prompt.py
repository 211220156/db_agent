from typing import Any

from prompt import *
from .. import ChainContext
from ..chain import Step
from ..step_output import StepOutput


class GeneratePrompt(Step):

    name = "GeneratePrompt"
    initial_prompt: str
    user_prompt: str = df_user_prompt

    def exec(self, input: Any, **kwargs) -> StepOutput:
        """
        生成Prompt，需要根据上下文中的记忆生成
        """

        # 提取出上下文信息
        context = kwargs.get("context")
        logger = kwargs.get("logger")

        self.initial_prompt = self.generate_prompt(input, context)

        prompt = self.initial_prompt if len(context.history) == 0 else self.user_prompt

        logger.log(f"Generate prompt: {prompt}")

        return StepOutput(
            prompt,
            "Prompt Generated Successfully",
            #
            # {"prompt": prompt},
        )

    def generate_dfs_desc(self, context: ChainContext) -> str:
        """
        生成 DataFrame 描述字符串，限制行数最多显示 5 行。

        Args:
            context (ChainContext): 包含多个 DataFrame 的上下文对象。

        Returns:
            str: 描述字符串。
        """
        dfs_desc = ""

        for i, df in enumerate(context.dfs):
            # 获取 DataFrame 的基本信息
            shape_info = f"{df.shape[0]}x{df.shape[1]}"
            headers = ",".join(df.columns)

            # 限制 rows 显示的行数至多为 5 行
            limited_rows_df = df.head(5)  # 获取前 5 行
            rows = limited_rows_df.to_string(index=False, header=False)  # 格式化行数据，不包含索引和列名

            # 拼接成指定格式
            dataframe_str = (
                f"<dataframe>\n"
                f"dfs[{i}]:{shape_info}\n"
                f"{headers}\n\n"
                f"{rows}\n"
                f"</dataframe>\n"
            )
            dfs_desc += dataframe_str

        return dfs_desc

    def generate_prompt(self, input: Any, context: ChainContext) -> str:
        """
        生成prompt。把上下文信息填充到prompt.py中的模板里。
        """
        # 默认使用df_prompt_template
        dfs_desc = self.generate_dfs_desc(context)

        initial_prompt = DF_PROMPT.format(dfs_desc=dfs_desc)

        prompt = df_prompt_template.format(
            initial_prompt=initial_prompt,
            tools_desc=context.get_tools_desc(),
            query=input,
            # agent_scratch=context.get("agent_scratch"),
            response_format=df_response_format
        )

        return prompt