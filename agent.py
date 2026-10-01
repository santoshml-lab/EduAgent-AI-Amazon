from groq import Groq
import os
import json

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

        # Ask the AI to identify the user's intent
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": """
You are the tool-selection brain of EduAgent AI.

Choose exactly one action:

1. study_plan
2. learning_resources
3. calculator
4. general

Return ONLY valid JSON.

For study_plan:
{"action":"study_plan","topic":"Python","days":7}

For learning_resources:
{"action":"learning_resources","topic":"Python"}

For calculator:
{"action":"calculator","expression":"125*48"}

For general:
{"action":"general"}

Do not include Markdown.
Do not explain your decision.
"""
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            temperature=0,
            max_tokens=200
        )

        ai_text = response.choices[0].message.content.strip()

        # Convert AI response into JSON
        try:
            decision = json.loads(ai_text)
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "AI returned an invalid tool decision.",
                "raw_response": ai_text
            }

        action = decision.get("action")

        # Execute selected tool
        if action == "study_plan":
            topic = decision.get("topic", "General")
            days = decision.get("days", 7)

            return study_plan(topic, days)

        if action == "learning_resources":
            topic = decision.get("topic", "General")

            return learning_resources(topic)

        if action == "calculator":
            expression = decision.get("expression", "")

            return calculate(expression)

        # General AI response
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are EduAgent AI, an educational AI assistant. "
                        "Give concise, clear and helpful answers."
                    )
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            temperature=0.2,
            max_tokens=300
        )

        return {
            "status": "success",
            "agent": self.name,
            "action": "general",
            "response": response.choices[0].message.content
        }
