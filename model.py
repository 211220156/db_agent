import os, json
# from openai import OpenAI

import dashscope
from prompt import user_prompt
from dashscope.api_entities.dashscope_response import Message


class Model(object):
    def __init__(self):
        self.api_key = os.environ.get('DASH_SCOPE_API_KEY')
        self.model_name = os.environ.get('MODEL_NAME')
        self._client = dashscope.Generation()
        # self._client = OpenAI(
        #     api_key=os.environ['OPENAI_API_KEY'],
        #     base_url=os.environ['OPENAI_BASE_URL']
        # )
        self.max_retry_time = 5

    def chat(
        self,
        prompt,
        chat_history,
    ):
        cur_retry_time = 0
        while cur_retry_time < self.max_retry_time:
            cur_retry_time += 1
            try:
                messages = [
                    # {"role": "system", "content": prompt}
                    Message(role="system", content=prompt)
                ]
                for his in chat_history:
                    messages.append(Message(role="user", content=his[0]))
                    messages.append(Message(role="assistant", content=his[1]))
                    messages.append(Message(role="assistant", content=his[2]))
                    # messages.append({"role": "user", "content": his[0]})
                    # messages.append({"role": "system", "content": his[1]})

                # 最后1条信息是用户的输入
                messages.append(Message(role="user", content=user_prompt))
                # messages.append({"role": "user", "content": user_prompt})

                # create_params = {
                #     "model": self.model_name,
                #     "messages": messages,
                #     "tools": functions_to_json(),
                #     "tool_choice": tool_choice,
                #     "stream": stream,
                # }
                response = self._client.call(
                    model=self.model_name,
                    api_key=self.api_key,
                    messages=messages
                )
                print("response:{}".format(response))
                content = json.loads(response["output"]["text"])

                # completion = self._client.chat.completions.create(**create_params)
                # message = completion.choices[0].message
                # print("message:", message)
                return content
                # if isinstance(message.content, str):
                #     print("message.content:", message.content)
                # return json.loads(message.content)
            except Exception as e:
                print("call llm exception:{}".format(e))
        return {}
