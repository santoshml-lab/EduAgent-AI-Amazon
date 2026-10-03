import os
import json
import urllib.request
import urllib.error


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


def web_search(query: str):
    """
    Search the web using the Tavily Search API.
    """

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return {
            "tool": "web_search",
            "query": query,
            "error": "TAVILY_API_KEY is not configured."
        }

    url = "https://api.tavily.com/search"

    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "include_answer": True,
        "max_results": 5
    }

    try:
        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

        return {
            "tool": "web_search",
            "query": query,
            "answer": result.get("answer"),
            "results": result.get("results", [])
        }

    except urllib.error.HTTPError as error:
        return {
            "tool": "web_search",
            "query": query,
            "error": f"Tavily API error: {error.code}"
        }

    except Exception as error:
        return {
            "tool": "web_search",
            "query": query,
            "error": f"Web search failed: {str(error)}"
        }
