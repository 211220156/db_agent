
df_response_format = """
    {
        "code": "```python The python code you want to execute in markdown format ```",
        "finish": "`True` or `False` as a string, represent the status of this question. If you have got the final answer of user's question, set this flag `True`, otherwise `False`.",
        "answer": "The answer you will reply to user. When you finish the question, set 'finish' True and set this variable.",
        "thoughts": {
            "plan": "Simply describe short-term and long-term plan lists",
            "criticism": "Constructive self-criticism",
            "speak": "A summary of the current step returned to the user",
            "reasoning": "reasoning"
        },
        "observation": "Observe the overall progress of the current task"
    }
"""

df_expected_format = {
    "code": str,  # 要执行的 Python 代码
    "finish": str,  # 布尔值，表示问题的状态。如果已获得最终答案，设置为 True，否则为 False
    "answer": str,  # 回复用户的答案。当问题结束时，设置 'finish' 为 True，并设置此变量
    "thoughts": {
        "plan": str,  # 简要描述短期和长期计划的列表
        "criticism": str,  # 建设性的自我批评
        "speak": str,  # 返回给用户的当前步骤总结
        "reasoning": str,  # 推理过程
    },
    "observation": str,  # 观察当前任务的整体进度
}

DF_PROMPT = """
You have a list of pandas' DataFrames, named dfs. Variable `dfs: list[pd.DataFrame]` is already declared.
You need to generate python code **in markdown format** according to the pandas documentation and return it to the user, who will execute it and inform you of the execution result. 
You then parse the results to determine whether the problem has been solved. 
If not, reflect and plan, regenerate the code, and repeat the process. 
Point to the result you think you have, and return the final answer to the user.
You can only use the existing DataFrames, you can't fudge the data.

{dfs_desc}

In your code, you must declare a result variable of type string to store the answer in. 
The code ends with `print(result)` as a statement.
"""


df_prompt_template = """
{initial_prompt}

The following utility functions are already defined and you can use them directly:
{tools_desc}
**Note: Do not define your own utility functions!!**

Question:
{query}

You should respond in json format, as follows:
{response_format}
Ensure that the response result can be loaded successfully by python json.loads().

"""

df_user_prompt = """
Based on the execution result of the previously generated code, determine whether the problem is resolved. 
If resolved, return the answer to the user in time; 
If the code execution is incorrect or the result is incorrect, regenerate the code.
"""