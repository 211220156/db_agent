from agent import Agent
from helpers.agent_function import AgentFunction
import pandas as pd

# 定义工具函数
def get_mood_by_name(name: str) -> str:
    """
    Get someone's mood by name.

    Args:
        name: The person's name.
    Returns:
        The person's mood.
    """
    return "very happy"

employees_data = { "EmployeeID": [1, 2, 3, 4, 5], "Name": ["John", "Emma", "Liam", "Olivia", "William"], "Department": ["HR", "Sales", "IT", "Marketing", "Finance"],}

salaries_data = { "EmployeeID": [1, 2, 3, 4, 5], "Salary": [5000, 6000, 4500, 7000, 5500], }

employees_df = pd.DataFrame(employees_data)
salaries_df = pd.DataFrame(salaries_data)

agent = Agent(
    dfs=[employees_df, salaries_df],
    tools=[AgentFunction(get_mood_by_name)]
)
print(agent.run("What's the mood of the top earner?"))

