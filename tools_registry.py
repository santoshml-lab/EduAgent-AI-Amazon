from tool import ToolManager
from calculator_tool import calculator


def create_tool_manager():
    """
    Create and configure the ToolManager.
    """

    manager = ToolManager()

    manager.register_tool("calculator", calculator)

    return manager
