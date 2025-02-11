from typing import Any, Optional, Dict
import re, sys, ast
from contextlib import redirect_stdout
from io import StringIO

from ..chain import Step
from ..step_output import StepOutput

class ExecuteCode(Step):

    name = "ExecuteCode"

    def _sanitize_input(self, query: str) -> str:
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

    def _run_python_code(
        self,
        query: str,
        globals: Optional[Dict] = None,
        locals: Optional[Dict] = None,
    ) -> str:
        """
        运行python代码
        """
        if sys.version_info < (3, 9):
            return (
                "This tool relies on Python 3.9 or higher "
                "(as it uses new functionality in the `ast` module, "
                f"you have Python version: {sys.version}"
            )
        try:
            query = self._sanitize_input(query)
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

    def exec(self, input: Any, **kwargs) -> StepOutput:
        """
        执行上一步生成的代码。
        """
        context = kwargs.get("context")
        logger = kwargs.get("logger")

        # 把工具函数、数据添加到globals
        globals = {"dfs": context.dfs}
        for tool in context.tools:
            globals[tool.name] = tool

        output = self._run_python_code(input, globals=globals)
        # logger.log(f"Executing code with env {globals}, result: {output}")
        logger.log(f"Code Execution result: {output}")

        # 将结果放入context
        context.add("execution_result", output)

        return StepOutput(
            output=output,
            success=True,
            # TODO 仅用于测试，稍后删掉
            # finish=True
        )