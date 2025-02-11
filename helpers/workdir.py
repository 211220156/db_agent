import os

def get_workdir_root():
    """
    从环境变量获取工作目录
    """
    workdir_root = os.environ.get('WORKDIR_ROOT')
    return workdir_root