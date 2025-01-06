from agent import Agent
from prompt import CSV_PROMPT, MYSQL_PROMPT
from tools import *
import pandas as pd

def create_csv_agent(
    data_path: str,
    debug: bool = False,
) -> Agent:
    """
    创建一个处理csv数据的agent。提供csv文件的路径，用pandas处理后将DataFrame传入agent
    """
    return Agent(
        functions=[create_shell(locals={"df": pd.read_csv(data_path).fillna(value=0)})],
        initial_prompt=CSV_PROMPT,
        debug=debug,
    )

def create_sql_agent(
    host: str,
    user: str,
    password: str,
    database: str,
    debug: bool = False
):
    """
    创建一个与MySQL沟通的agent。
    """
    return Agent(
        functions=mysql_tools(host, user, password, database),
        initial_prompt=MYSQL_PROMPT,
        debug=debug,
    )

def run_loop(agent):
    print("Starting CLI 🐝")

    while True:
        query = input("\033[90mUser\033[0m: ")

        if query.lower() in ["exit", "quit"]:
            print(f"\033[94m{"您已退出对话"}\033[0m")
            break

        agent.run(query)


if __name__ == "__main__":
    # 测试

    funcs = mysql_tools(
        host="127.0.0.1",
        user="root",
        password="root",
        database="demo",
    )

    get_table_names, get_column_names, get_database_info, execute = funcs[0], funcs[1], funcs[2], funcs[3]

    print(execute("SELECT COUNT(*) FROM employees"))

    print(execute("select * from employees where Salary>100000"))

