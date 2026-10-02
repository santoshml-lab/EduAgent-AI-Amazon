from tool import ToolManager
from tools import study_plan, learning_resources, calculate


def create_tool_manager():
    """
    Create and configure the ToolManager.
    """

    manager = ToolManager()

    manager.register_tool("study_plan", study_plan)
    manager.register_tool("learning_resources", learning_resources)
    manager.register_tool("calculator", calculate)

    return manager
