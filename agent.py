from groq import Groq
import os

from tools import study_plan, learning_resources, calculate


class EduAgent:

    def __init__(self):
        self.name = "EduAgent AI"
        self.description = (
            "An agentic AI learning assistant for study planning, "
            "educational support, research, and productivity."
        )

        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

    def process(self, user_input: str):

        text = user_input.lower()

        # Study plan tool
        if "study plan" in text or "study schedule" in text:
            topic = user_input
            return study_plan(topic, 7)

        # Learning resources tool
        if "resources" in text or "learn" in text:
            topic = user_input
            return learning_resources(topic)

        # Calculator tool
        if "calculate" in text:
            expression = user_input.replace("calculate", "").strip()
            return calculate(expression)

        # Default response
        return {
            "status": "success",
            "agent": self.name,
            "message": (
                "I can help with study plans, learning resources, "
                "and calculations."
            )
        }
