from tools_registry import create_tool_manager


def main():
    manager = create_tool_manager()

    print("Available tools:")
    print(manager.list_tools())

    result = manager.execute_tool(
        "calculator",
        {"expression": "125 * 48"}
    )

    print("\nCalculator result:")
    print(result)


if __name__ == "__main__":
    main()
