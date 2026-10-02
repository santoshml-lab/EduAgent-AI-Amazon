import os
import requests


def web_search(query: str):
    """
    Search the web using the Tavily API.
    """

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return {
            "success": False,
            "error": "TAVILY_API_KEY is not configured."
        }

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": 5
            },
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        results = []

        for item in data.get("results", []):
            results.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "content": item.get("content")
            })

        return {
            "success": True,
            "query": query,
            "results": results
        }

    except Exception as e:
        return {
            "success": False,
            "query": query,
            "error": str(e)
        }
