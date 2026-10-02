from typing import Any, Dict


class ToolManager:
    """
    Manages tools used by EduAgent AI.
    """

    def __init__(self):
        self.tools = {}

    def register_tool(self, name: str, tool):
        """Register a new tool."""
        self.tools[name] = tool

    def execute_tool(
        self,
        name: str,
        arguments: Dict[str, Any] | None = None
    ) -> Any:
        """Execute a registered tool."""

        if name not in self.tools:
            raise ValueError(f"Tool not found: {name}")

        tool = self.tools[name]

        if arguments is None:
            arguments = {}

        return tool(**arguments)

    def list_tools(self):
        """Return the list of available tools."""
        return list(self.tools.keys())
