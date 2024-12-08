import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    api_key="sk-rleivZCnFRtY44AybrrVjNXJC8l2OIoNj1sS2JEDFKKZCmz4",
    base_url="https://xiaoai.plus/v1",
    model="gpt-3.5-turbo",  # 选择模型名称，原生 OpenAI 中常见的模型是 gpt-3.5-turbo 或 gpt-4
    temperature=0.7          # 这个是可选的，控制输出的创造性
)

df = pd.read_csv("./data/data.csv").fillna(value=0) # pandas读取数据得到dataframe

agent = create_pandas_dataframe_agent(llm=model, df=df, verbose=True, allow_dangerous_code=True)

CSV_PROMPT_PREFIX ="""
First set the pandas display options to show all the columns,
get the column names, then answer the question.
"""

CSV_PROMPT_SUFFIX="""
- **ALWAYS** before giving the Final Answer, try another method.
Then reflect on the answers of the two methods you did and ask yourself
if it answers correctly the original question.
If you are not sure, try another method.
- If the methods tried do not give the same result,reflect and
try again until you have two methods that have the same result.
- If you still cannot arrive to a consistent result, say that
you are not sure of the answer.
- If you are sure of the correct answer, create a beautiful
and thorough response using Markdown.
- **DO NOT MAKE UP AN ANSWER OR USE PRIOR KNOWLEDGE,
ONLY USE THE RESULTS OF THE CALCULATIONS YOU HAVE DONE**.
- **ALWAYS**, as part of your "Final Answer", explain how you got
to the answer on a section that starts with: "\n\nExplanation:\n".
In the explanation, mention the column names that you used to get
to the final answer.
"""

QUESTION = "how many people live in San Francisco and under 50?" # 定义问题

print(agent.invoke(CSV_PROMPT_PREFIX + QUESTION + CSV_PROMPT_SUFFIX)['output'])
