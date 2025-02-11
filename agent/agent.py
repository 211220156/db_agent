from typing import List, Optional, Union
import pandas as pd

from chain import Chain, ChainContext
from chain.action_step.call_llm import CallLLM
from chain.action_step.execute_code import ExecuteCode
from chain.action_step.generate_prompt import GeneratePrompt
from chain.action_step.parse_result import ParseResult
from config import Config
from helpers.load_config import load_from_json
from logger import Logger

from helpers.agent_function import AgentFunction

class Agent:

    dfs: List[pd.DataFrame]
    tools: List[AgentFunction]
    chain: Chain
    config: Config
    context: ChainContext
    logger: Logger

    def __init__(
        self,
        dfs: Union[pd.DataFrame, str, List[Union[pd.DataFrame, str]]],
        tools: Optional[List[AgentFunction]] = None,
        config: Optional[Union[Config, dict]] = None,
        chain:  Optional[Chain] = None,
    ):
        self.dfs = self._get_dfs(dfs)
        self.config = self._get_config(config)
        self.tools = tools
        self.context = ChainContext(
            dfs=self.dfs,
            config=self.config,
            tools=self.tools,
        )


        self.logger = Logger(
            save_logs_to_file=self.config.save_logs_to_file, verbose=self.config.verbose
        )

        self.chain = (chain
            or
            Chain(
                context=self.context,
                steps=[
                    GeneratePrompt(),
                    CallLLM(),
                    ParseResult(),
                    ExecuteCode()
                ],
                logger=self.logger,
            )
        )

    def _get_config(self, config: Union[Config, dict]) -> Config:
        """
        若没有提供Config，从文件中读取
        """
        if isinstance(config, Config):
            return config

        return load_from_json(config)

    def _get_dfs(self, dfs: Union[pd.DataFrame, str, List[Union[pd.DataFrame, str]]]) -> List[pd.DataFrame]:
        """
        将潜在的csv文件转化为pd.DataFrame
        """
        ret = []

        if not isinstance(dfs, list):
            dfs = [dfs]

        for df in dfs:
            if isinstance(df, pd.DataFrame):
                ret.append(df)
            elif isinstance(df, str):
                # TODO 支持更多格式的文件
                ret.append(pd.read_csv(df))

        return ret

    def run(self, query: str):
        """
        向agent提问
        """
        try:
            self.logger.log(f"Question: {query}")
            self.logger.log(f"Agent is thinking with model type: {self.config.model.model_type}, model name: {self.config.model.model_name}")

            return self.chain.run(query)

        except Exception as e:
            return f"Sorry, I'm unable to answer your question due to exception: \n{e}\n"
