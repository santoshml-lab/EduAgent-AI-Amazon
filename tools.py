def study_plan(topic: str, days: int):
    """
    Create a structured day-by-day study plan.
    """

    days = max(1, min(days, 30))

    stages = [
        "Learn the fundamentals",
        "Understand important concepts",
        "Study practical examples",
        "Practice problems",
        "Apply the concepts",
        "Build a small practical task",
        "Review and revise"
    ]

    plan = []

    for day in range(1, days + 1):
        stage = stages[(day - 1) % len(stages)]

        plan.append({
            "day": day,
            "topic": topic,
            "focus": stage,
            "task": f"{stage} of {topic}"
        })

    return {
        "tool": "study_plan",
        "topic": topic,
        "days": days,
        "plan": plan,
        "message": f"{days}-day study plan created for {topic}."
    }


def learning_resources(topic: str):
    """
    Provide structured learning resources for a topic.
    """

    return {
        "tool": "learning_resources",
        "topic": topic,
        "resources": [
            {
                "type": "fundamentals",
                "title": f"Beginner concepts of {topic}",
                "purpose": "Build a strong foundation."
            },
            {
                "type": "practice",
                "title": f"Practice questions for {topic}",
                "purpose": "Strengthen understanding through practice."
            },
            {
                "type": "revision",
                "title": f"Revision notes for {topic}",
                "purpose": "Review important concepts quickly."
            },
            {
                "type": "project",
                "title": f"Mini project using {topic}",
                "purpose": "Apply the concepts in a practical task."
            }
        ]
    }


def calculate(expression: str):
    """
    Calculate a mathematical expression safely.
    """

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
