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

- study_plan
- learning_resources
- calculator
- general

Return ONLY one valid JSON object.

Rules:

If the user wants a study plan, return:
{"action":"study_plan","topic":"<actual topic>","days":7}

If the user wants learning resources, return:
{"action":"learning_resources","topic":"<actual topic>"}

If the user asks for a calculation, return:
{"action":"calculator","expression":"<mathematical expression>"}

For any other request, return:
{"action":"general"}

IMPORTANT:
- Replace <actual topic> with the topic requested by the user.
- Do NOT always use Python.
- Do NOT explain your decision.
- Do NOT return Markdown.
- Return JSON only.
""",
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            temperature=0,
            max_tokens=100
        )

        message = response.choices[0].message

        ai_text = (message.content or "").strip()

        if not ai_text:
            return {
                "status": "error",
                "message": "AI returned an empty tool decision.",
                "finish_reason": response.choices[0].finish_reason,
                "response": str(message)
            }

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
                        "Give concise, clear and helpful answers. "
                        "Return the answer as valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            temperature=0.2,
            max_tokens=300,
            response_format={"type": "json_object"},
        )

        return {
            "status": "success",
            "agent": self.name,
            "action": "general",
            "response": response.choices[0].message.content
        }
