import os, sys
import re
import ast
from contextlib import redirect_stdout
from io import StringIO
from langchain_community.tools.tavily_search import TavilySearchResults
import mysql.connector
from typing import Optional, Dict

def _get_workdir_root():
    workdir_root = os.environ.get('WORKDIR_ROOT', "./data")
    return workdir_root


WORKDIR_ROOT = _get_workdir_root()

def sanitize_input(query: str) -> str:
    """
    清理输入

    删除空格，反勾号和python（如果llm错误地将python控制台作为终端）

    Args:
        query：要清理的查询

    Returns:
        str: 经过处理的查询
    """

    # Removes `, whitespace & python from start
    query = re.sub(r"^(\s|`)*(?i:python)?\s*", "", query)
    # Removes whitespace & ` from end
    query = re.sub(r"(\s|`)*$", "", query)
    return query

def create_shell(
    globals: Optional[Dict] = {},
    locals: Optional[Dict] = {}
):
    """
    通过闭包传递变量，使得下面的函数run_python_code具备python shell的local、global变量，便于操作数据。
    """
    def run_python_code(
        query: str,
    ) -> str:
        """
        一个Python shell。使用它来执行python命令，特别是当您需要调用对象的函数时。
        输入应该是一个有效的python命令。
        使用此工具时，有时会简化输出
        在你的回答中使用它之前，确保它看起来不缩写。

        :param query:
        :return:
        """
        if sys.version_info < (3, 9):
            return (
                "This tool relies on Python 3.9 or higher "
                "(as it uses new functionality in the `ast` module, "
                f"you have Python version: {sys.version}"
            )
        try:
            query = sanitize_input(query)
            tree = ast.parse(query)
            module = ast.Module(tree.body[:-1], type_ignores=[])
            # exec不返回值
            exec(ast.unparse(module), globals, locals)  # type: ignore
            module_end = ast.Module(tree.body[-1:], type_ignores=[])
            module_end_str = ast.unparse(module_end)  # type: ignore
            io_buffer = StringIO()
            try:
                with redirect_stdout(io_buffer):
                    # eval返回值，写入io_buffer
                    ret = eval(module_end_str, globals, locals)
                    if ret is None:
                        return io_buffer.getvalue()
                    else:
                        return ret
            except Exception:
                with redirect_stdout(io_buffer):
                    exec(module_end_str, globals, locals)
                return io_buffer.getvalue()
        except Exception as e:
            return "{}: {}".format(type(e).__name__, str(e))

    return run_python_code


def read_file(filename) -> str:
    """
    读文件
    """
    filename = os.path.join(WORKDIR_ROOT, filename)
    if not os.path.exists(filename):
        return f"{filename} not exit, please check file exist before read"
    with open(filename, 'r', encoding="utf-8") as f:
        return "\n".join(f.readlines())


def append_to_file(filename, content) -> str:
    """
    追加内容到文件
    """
    filename = os.path.join(WORKDIR_ROOT, filename)
    if not os.path.exists(filename):
        f"{filename} not exit, please check file exist before read"
    with open(filename, 'a') as f:
        f.write(content)
    return "append_content to file success."


def write_to_file(filename, content) -> str:
    """
    写文件，需要保存llm输出到文件时用到
    """
    filename = os.path.join(WORKDIR_ROOT, filename)
    if not os.path.exists(WORKDIR_ROOT):
        os.makedirs(WORKDIR_ROOT)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return "write content to file success."


def search(query) -> str:
    """
    这是一个搜索引擎，你可以通过这个搜索引擎获得额外的知识
    """
    daily = TavilySearchResults(max_results=5)
    try:
        ret = daily.invoke(input=query)
        print("搜索结果:{}".format(ret))
        print("\n")
        content_list = []
        """
        # 从哪个网站上获取的内容
        ret = [
            {
                "content": "",
                "url": ""
            }
        ]
        """
        for obj in ret:
            content_list.append(obj["content"])
        return "\n".join(content_list)
    except Exception as e:
        return "search error:{}".format(e)


def mysql_tools(
    host: str,
    user: str,
    password: str,
    database: str
):
    # 创建数据库连接
    db = mysql.connector.connect(
        host=host,  # MySQL服务器地址
        user=user,  # 用户名
        password=password,  # 密码
        database=database  # 数据库名称
    )

    # 创建游标对象，用于执行SQL查询
    cursor = db.cursor()

    # 闭包工具函数
    def get_table_names():
        """
        返回所有表名.
        """
        table_names = []
        # 查询 MySQL 数据库中的所有表名
        cursor.execute("SHOW TABLES;")
        for table in cursor.fetchall():
            table_names.append(table[0])  # MySQL 的 SHOW TABLES 返回的是元组，表名在第一个元素
        return table_names

    def get_column_names(table_name):
        """
        返回所有列名.
        """
        column_names = []
        # 查询指定表的所有列信息
        cursor.execute(f"SHOW COLUMNS FROM `{table_name}`;")
        for col in cursor.fetchall():
            column_names.append(col[0])  # SHOW COLUMNS 返回的元组，第一个元素是列名
        return column_names


    def get_database_info():
        """
        返回一个包含数据库中每个表的名字和列的字典列表。
        """
        table_dicts = []
        for table_name in get_table_names():
            columns_names = get_column_names(table_name)
            table_dicts.append({"table_name": table_name, "column_names": columns_names})
        return table_dicts

    def execute(query):
        """
        执行数据库语句
        :param query: 要执行的 SQL 查询语句
        :return: 查询结果
        """
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            db.commit()
        except Exception as e:
            result = f"执行查询时出错: {e}"
            print(result)

        return result

    return [get_table_names, get_column_names, get_database_info, execute]


# 工具函数的description，用于Agent生成tools的描述
tools_info = [
    {
        "name": "read_file",
        "description": "read file form agent generate, should write file before read",
        "args": [
            {
                "name": "filename",
                "type": "string",
                "description": "read file name"
            }
        ]
    },
    {
        "name": "append_to_file",
        "description": "append llm content to file, should write file before read",
        "args": [
            {
                "name": "filename",
                "type": "string",
                "description": "file name"
            },
            {
                "name": "content",
                "type": "string",
                "description": "append to file content"
            }
        ]
    },
    {
        "name": "write_to_file",
        "description": "write llm content to file",
        "args": [
            {
                "name": "filename",
                "type": "string",
                "description": "file name"
            },
            {
                "name": "content",
                "type": "string",
                "description": "write to file content"
            }
        ]
    },
    {
        "name": "finish",
        "description": "Finish user's question",
        "args": [
            {
                "name": "answer",
                "type": "string",
                "description": "the final answer"
            }
        ]
    },
    {
        "name": "search",
        "description": "this is a search engine, you can gain additional knowledge through this search engine "
                       "when you are unsure of large model return",
        "args": [
            {
                "name": "query",
                "type": "string",
                "description": "search query to look up"
            }
        ]
    },
    {
        "name": "run_python_code",
        "description": "A Python shell. Use this to execute python commands, especially when you need to call an object's functions."
                        "Input should be a valid python command.",
        "args": [
            {
                "name": "query",
                "type": "string",
                "description": "The python code you want to execute"
            }
        ]
    },
    {
        "name": "get_table_names",
        "description": "Get all the table names in this database",
        "args": []
    },
    {
        "name": "get_column_names",
        "description": "Get all column names in a table.",
        "args": [
            {
                "name": "table_name",
                "type": "string",
                "description": "The table name you want to look up"
            }
        ]
    },
    {
        "name": "get_database_info",
        "description": "Get all column names for all tables in the database. Returns a dict"
                       "where key is the table name and value is all the column names of the table.",
        "args": []
    },
    {
        "name": "execute",
        "description": "A MySQL command line. You can execute MySQL command through this function."
                       "The input must be a valid MySQL command.",
        "args": [
            {
                "name": "query",
                "type": "string",
                "description": "The MySQL command you want to execute"
            }
        ]
    }
]


