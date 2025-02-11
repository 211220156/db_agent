from dotenv import find_dotenv, load_dotenv
from exceptions import LoadEnvError


def load_env():
    """
    加载环境变量
    """
    dotenv_path = find_dotenv()
    if dotenv_path:
        load_dotenv(dotenv_path)
    else:
        raise LoadEnvError("No .env file found")