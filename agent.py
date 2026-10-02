from groq import Groq
import os
import json

from tools_registry import create_tool_manager


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

        self.tool_manager = create_tool_manager()

    def process(self, user_input: str):

        # Step 1: Ask the AI to identify the user's intent
        decision_response = self.client.chat.completions.create(
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

If the user wants a study plan:
{"action":"study_plan","topic":"<actual topic>","days":7}

If the user wants learning resources:
{"action":"learning_resources","topic":"<actual topic>"}

If the user asks for a calculation:
{"action":"calculator","expression":"<mathematical expression>"}

For any other request:
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

        message = decision_response.choices[0].message
        ai_text = (message.content or "").strip()

        # Step 2: Validate the AI decision
        if not ai_text:
            return {
                "status": "error",
                "agent": self.name,
                "message": "AI returned an empty tool decision.",
                "finish_reason": decision_response.choices[0].finish_reason
            }

        try:
            decision = json.loads(ai_text)
        except json.JSONDecodeError:
            return {
                "status": "error",
                "agent": self.name,
                "message": "AI returned an invalid tool decision.",
                "raw_response": ai_text
            }

        action = decision.get("action")

        # Step 3: Execute the selected tool
        if action == "study_plan":
            tool_result = self.tool_manager.execute_tool(
                "study_plan",
                {
                    "topic": decision.get("topic", "General"),
                    "days": decision.get("days", 7)
                }
            )

            return self.build_tool_response(
                user_input,
                action,
                tool_result
            )

        if action == "learning_resources":
            tool_result = self.tool_manager.execute_tool(
                "learning_resources",
                {
                    "topic": decision.get("topic", "General")
                }
            )

            return self.build_tool_response(
                user_input,
                action,
                tool_result
            )

        if action == "calculator":
            tool_result = self.tool_manager.execute_tool(
                "calculator",
                {
                    "expression": decision.get("expression", "")
                }
            )

            return self.build_tool_response(
                user_input,
                action,
                tool_result
            )

        # Step 4: General AI response
        if action == "general":
            return self.general_response(user_input)

        # Step 5: Handle unexpected actions
        return {
            "status": "error",
            "agent": self.name,
            "message": "AI selected an unknown action.",
            "action": action
        }

    def build_tool_response(
        self,
        user_input: str,
        action: str,
        tool_result
    ):
        """
        Convert the tool result into a natural agent response.
        """

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": """
You are EduAgent AI.

You have just executed a tool.

Use the tool result to answer the user's request naturally.

Rules:
- Be concise and helpful.
- Do not mention internal implementation details.
- Do not invent information.
- Use only information available in the tool result.
- Return valid JSON.
"""
                },
                {
                    "role": "user",
                    "content": json.dumps({
                        "user_request": user_input,
                        "selected_action": action,
                        "tool_result": tool_result
                    })
                }
            ],
            temperature=0.2,
            max_tokens=300,
            response_format={"type": "json_object"},
        )

        return {
            "status": "success",
            "agent": self.name,
            "action": action,
            "tool_result": tool_result,
            "response": response.choices[0].message.content
        }

    def general_response(self, user_input: str):

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
