import logging
import sys
from typing import List
from helpers import concat_path

class Logger:
    """
    打印日志的类
    _verbose: 为True则额外输出到控制台
    _save_logs_to_file: 为True则保存到文件中。默认路径为agent.log
    """
    _logger: logging.Logger
    _logs: List[str]
    _verbose: bool
    _save_logs_to_file: bool
    _filename: str

    def __init__(self, verbose: bool = False, save_logs_to_file: bool = True, filename: str = "agent.log"):
        self._logger = logging.getLogger()
        self._logs = []
        self._verbose = verbose
        self._save_logs_to_file = save_logs_to_file
        self._filename = filename

        handlers = []
        if save_logs_to_file:
            filepath = concat_path(filename)
            handlers.append(logging.FileHandler(filepath))

        if verbose:
            handlers.append(logging.StreamHandler(sys.stdout))

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=handlers,
        )

    def log(self, message: str, level: int = logging.INFO):

        self._logs.append(message)

        if level == logging.INFO:
            self._logger.info(message)
        elif level == logging.WARNING:
            self._logger.warning(message)
        elif level == logging.ERROR:
            self._logger.error(message)
        elif level == logging.CRITICAL:
            self._logger.critical(message)

