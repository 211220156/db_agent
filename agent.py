import time
from datetime import datetime
import json
from tools import tools_info
from prompt import *
from model import Model
from dotenv import load_dotenv
from typing import Callable, List
load_dotenv()

"""
本质流程：
                |<-------------------------------- 否 --------------------------<-|
                |                                                                 |
提问 -> 是否继续(超时？超过最大次数？)  --继续--> 结合上一步输出，整体反思、规划， ---> 判断是否已经得出答案  
                |                          使用对应工具执行对应动作                    |
                | 不继续                                                       是   |
                |------------------------------>  结束  <--------------------------|
"""

"""
response格式: 
{
    "action": {
        "name": "action name",
        "args": {
            "args name": "args value"
        }
    },
    "thoughts":{
        "plan": "Simply describe short-term and long-term plan lists",
        "criticism": "Constructive self-criticism",
        "speak": "A summary of the current step returned to the user",
        "reasoning": "reasoning"
    },
    "observation": "Observe the overall progress of the current task"
}
"""

expected_format = {
    "action": {
        "name": str,
        "args": {
            str: str,  # args 是一个字典，键和值均为字符串
        },
    },
    "thoughts": {
        "plan": str,
        "criticism": str,
        "speak": str,
        "reasoning": str,
    },
    "observation": str,
}


class Agent:
    def __init__(
        self,
        name: str = "Agent",
        model: Model = None,
        functions: List[Callable] = None,
        initial_prompt: str = INITIAL_PROMPT,
        max_request_time: int = 10,
        debug: bool = False,
    ):
        self.name = name
        self.model = model if model is not None else Model()
        self.functions = functions if functions is not None else []
        self.initial_prompt = initial_prompt
        self.max_request_time = max_request_time
        self.funcs_desc = self.gen_funcs_desc()
        self.debug = debug

    @staticmethod
    def parse_thoughts(response) -> str:
        try:
            thoughts = response.get("thoughts")
            observation = response.get("observation")
            plan = thoughts.get("plan")
            criticism = thoughts.get("criticism")
            speak = thoughts.get("speak")
            reasoning = thoughts.get("reasoning")
            prompt = f"plan: {plan}\ncriticism: {criticism}\nspeak: {speak}\nreasoning: {reasoning}\nobservation: {observation}"
            # print("parse_thoughts:" , prompt)
            return prompt
        except Exception as e:
            print("parse_thoughts error:{}".format(e))
            return "".format(e)

    @staticmethod
    def should_continue(action) -> bool:
        return not action.get("name") == "finish"

    @staticmethod
    def parse_answer(action) -> str:
        return action.get("args").get("answer")

    @staticmethod
    def validate(obj, format_spec):
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
                if not Agent.validate(value, expected_type):
                    return False
            else:
                # 无效的格式规范
                return False

        return True

    def print_answer(self, final_answer):
        """
        模拟打字效果，输出答案
        """
        print(f"\033[92m{self.name}: \033[0m", end='')
        for char in final_answer:
            print(char, end='', flush=True)  # end='' 确保不换行，flush=True 强制输出
            time.sleep(0.15)  # 每个字符间的延时
        print()  # 输出一个换行，结束后确保输出不被压在同一行


    def debug_print_response(
        self,
        response: dict
    ):
        if not self.debug:
            return

        thoughts = response.get("thoughts")
        observation = response.get("observation")
        plan = thoughts.get("plan")
        reasoning = thoughts.get("reasoning")
        speak = thoughts.get("speak")
        criticism = thoughts.get("criticism")
        print(f"\033[94mPlan: \033[0m{plan}")
        print(f"\033[94mCriticism: \033[0m{criticism}")
        print(f"\033[94mSpeak: \033[0m{speak}")
        print(f"\033[94mReasoning: \033[0m{reasoning}")
        print(f"\033[94mObservation: \033[0m{observation}")

        action_info = response.get("action")
        name, args = action_info["name"], action_info["args"]
        arg_str = json.dumps(args).replace(":", "=")
        print(f"\033[94mAction: \033[95m{name}\033[0m({arg_str[1:-1]})")

    def gen_funcs_desc(self) -> str:
        """
        生成函数描述
        :return:
        """
        funcs_name = ["finish"]
        for function in self.functions:
            funcs_name.append(function.__name__)

        funcs_desc = []
        for name in funcs_name:
            for idx, t in enumerate(tools_info):
                if name != t["name"]:
                    continue

                args_desc = []
                for info in t["args"]:
                    args_desc.append({
                        "name": info["name"],
                        "description": info["description"],
                        "type": info["type"]
                    })
                args_desc = json.dumps(args_desc, ensure_ascii=False)
                func_desc = f"{idx + 1}.{t['name']}:{t['description']}, args: {args_desc}"
                funcs_desc.append(func_desc)


        funcs_prompt = "\n".join(funcs_desc)
        return funcs_prompt


    def get_prompt(
        self,
        query: str,
        agent_scratch: str
    ) -> str:
        """
        生成prompt
        """
        prompt = prompt_template.format(
            initial_prompt=self.initial_prompt,
            query=query,
            constraints=constraints,
            actions=self.funcs_desc,
            resources=resources,
            best_practices=best_practices,
            agent_scratch=agent_scratch,
            response_format_prompt=response_format_prompt
        )
        return prompt

    def handle_func_call(
        self,
        action: dict
    ):
        """
        处理Model触发的function call.
        逐一比对函数名，找到对应的函数，并调用
        """
        func_name = action.get("name")
        args = action.get("args")

        for function in self.functions:
            if function.__name__ != func_name:
                continue
            try:
                result = function(**args)
            except Exception as e:
                print("调用工具异常:{}".format(e))
                result = "{}".format(e)
            return result

        result = "工具不存在:{}".format(func_name)
        print(result)
        return result



    def run(
        self,
        query: str
    ):
        """
        处理提问
        """
        cur_request_time = 0
        chat_history = []
        agent_scratch = ""
        final_answer = ""
        while cur_request_time < self.max_request_time:
            cur_request_time += 1

            prompt = self.get_prompt(query, agent_scratch)
            start_time = time.time()
            print(f"\033[90m[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][第{cur_request_time}次调用Model...]") if self.debug else None

            response = self.model.chat(prompt, chat_history)

            end_time = time.time()
            print(f"\033[90m[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][结束第{cur_request_time}次调用，耗时{end_time-start_time}秒]") if self.debug else None

            # 首先check大模型的回复是否满足格式要求
            if not self.validate(response, expected_format):
                # 不满足格式要求，重新调用llm
                print("call llm exception, response is :", response)
                continue

            # 提取大模型的回复，并输出
            self.debug_print_response(response)

            action = response.get("action")

            # 根据action判断是否结束
            if not self.should_continue(action):
                # 最终将结果返回给用户
                final_answer = self.parse_answer(action)
                break

            assistant_msg = self.parse_thoughts(response)


            call_function_result = self.handle_func_call(action)

            observation = response.get("observation")
            # 函数返回的结果
            agent_scratch = agent_scratch + "\nobservation:{}\nexecute action result: {}".format(observation,
                                                                                                    call_function_result)
            print(f"\033[94mAgent_scratch: \033[0m{agent_scratch}") if self.debug else None

            # 将上一步的observation、函数执行结果放入聊天记录中，形成短期记忆，下一次调用llm时，就能获取到之前的交流
            result = "This is the result of this action {}:{}".format(action.get("name"), call_function_result)
            chat_history.append([user_prompt, result, assistant_msg])

            final_answer = f"{observation}\n{call_function_result}" # 兜底的答案，取最后一次调用的结果。


        self.print_answer(final_answer)

if __name__ == "__main__":
    # 测试
    response = {
        'action': {
            'name': 'run_python_code',
            'args': {
                'query': 'df.shape[0]'
            }
        },
        'thoughts': {
            'plan': 'Calculate the number of rows in the DataFrame',
            'criticism': 'No need for complex actions, a simple code execution will suffice',
            'speak': 'Determining the number of rows in the DataFrame',
            'reasoning': 'Using df.shape[0] to get the count of rows is the most straightforward method'
        },
        'observation': 'Awaiting the result of the Python code execution to provide the number of rows'
    }
    print(Agent.validate(response, expected_format))