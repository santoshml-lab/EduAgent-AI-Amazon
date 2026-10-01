def study_plan(topic: str, days: int):
    return {
        "tool": "study_plan",
        "topic": topic,
        "days": days,
        "message": f"Study plan created for {topic} for {days} days."
    }


def learning_resources(topic: str):
    return {
        "tool": "learning_resources",
        "topic": topic,
        "resources": [
            f"Beginner concepts of {topic}",
            f"Practice questions for {topic}",
            f"Revision notes for {topic}"
        ]
    }


def calculate(expression: str):
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return {
            "tool": "calculator",
            "expression": expression,
            "result": result
        }
    except Exception:
        return {
            "tool": "calculator",
            "expression": expression,
            "error": "Invalid mathematical expression."
        }
