def calculator(expression: str):
    """
    Calculate a mathematical expression.
    """

    try:
        result = eval(expression, {"__builtins__": {}})
        return {
            "success": True,
            "expression": expression,
            "result": result
        }

    except Exception as e:
        return {
            "success": False,
            "expression": expression,
            "error": str(e)
        }
