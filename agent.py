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

        trace = [
            {
                "step": 1,
                "stage": "request",
                "message": "User request received."
            }
        ]

        decision = self.get_tool_decision(user_input)

        if decision is None:

            trace.append({
                "step": 2,
                "stage": "intent_detection",
                "message": "Unable to determine user intent."
            })

            return {
                "status": "error",
                "agent": self.name,
                "message": "AI could not determine the user's intent.",
                "trace": trace
            }

        action = decision.get("action")

        trace.append({
            "step": 2,
            "stage": "intent_detection",
            "message": f"Intent detected: {action}."
        })

        if action == "study_plan":

            trace.append({
                "step": 3,
                "stage": "tool_selection",
                "message": "Study Plan Tool selected."
            })

            tool_result = self.tool_manager.execute_tool(
                "study_plan",
                {
                    "topic": decision.get(
                        "topic",
                        "General"
                    ),
                    "days": decision.get(
                        "days",
                        7
                    )
                }
            )

            trace.append({
                "step": 4,
                "stage": "tool_execution",
                "message": (
                    "Study Plan Tool executed successfully."
                )
            })

            result = self.build_tool_response(
                user_input,
                action,
                tool_result
            )

            result["trace"] = trace + [
                {
                    "step": 5,
                    "stage": "response",
                    "message": "AI response generated."
                }
            ]

            return result

        if action == "learning_resources":

            trace.append({
                "step": 3,
                "stage": "tool_selection",
                "message": (
                    "Learning Resources Tool selected."
                )
            })

            tool_result = self.tool_manager.execute_tool(
                "learning_resources",
                {
                    "topic": decision.get(
                        "topic",
                        "General"
                    )
                }
            )

            trace.append({
                "step": 4,
                "stage": "tool_execution",
                "message": (
                    "Learning Resources Tool "
                    "executed successfully."
                )
            })

            result = self.build_tool_response(
                user_input,
                action,
                tool_result
            )

            result["trace"] = trace + [
                {
                    "step": 5,
                    "stage": "response",
                    "message": "AI response generated."
                }
            ]

            return result

        if action == "calculator":

            trace.append({
                "step": 3,
                "stage": "tool_selection",
                "message": "Calculator Tool selected."
            })

            tool_result = self.tool_manager.execute_tool(
                "calculator",
                {
                    "expression": decision.get(
                        "expression",
                        ""
                    )
                }
            )

            trace.append({
                "step": 4,
                "stage": "tool_execution",
                "message": (
                    "Calculator Tool executed successfully."
                )
            })

            result = self.build_tool_response(
                user_input,
                action,
                tool_result
            )

            result["trace"] = trace + [
                {
                    "step": 5,
                    "stage": "response",
                    "message": "AI response generated."
                }
            ]

            return result

        if action == "web_search":

            trace.append({
                "step": 3,
                "stage": "tool_selection",
                "message": "Web Search Tool selected."
            })

            tool_result = self.tool_manager.execute_tool(
                "web_search",
                {
                    "query": decision.get(
                        "query",
                        user_input
                    )
                }
            )

            trace.append({
                "step": 4,
                "stage": "tool_execution",
                "message": (
                    "Web Search Tool executed successfully."
                )
            })

            result = self.build_tool_response(
                user_input,
                action,
                tool_result
            )

            result["trace"] = trace + [
                {
                    "step": 5,
                    "stage": "response",
                    "message": "AI response generated."
                }
            ]

            return result

        if action == "general":

            trace.append({
                "step": 3,
                "stage": "reasoning",
                "message": (
                    "General educational response selected."
                )
            })

            result = self.general_response(
                user_input
            )

            result["trace"] = trace + [
                {
                    "step": 4,
                    "stage": "response",
                    "message": "AI response generated."
                }
            ]

            return result

        trace.append({
            "step": 3,
            "stage": "error",
            "message": "Unknown action selected."
        })

        return {
            "status": "error",
            "agent": self.name,
            "message": "AI selected an unknown action.",
            "action": action,
            "trace": trace
        }

    def get_tool_decision(self, user_input: str):

        system_prompt = """
You are the tool-selection brain of EduAgent AI.

Choose exactly one action:

- study_plan
- learning_resources
- calculator
- web_search
- general

Return ONLY one valid JSON object.

Rules:

If the user wants a study plan:
{"action":"study_plan","topic":"<actual topic>","days":7}

If the user wants learning resources:
{"action":"learning_resources","topic":"<actual topic>"}

If the user asks for a calculation:
{"action":"calculator","expression":"<mathematical expression>"}

If the user asks to search the web, find current information,
look up recent news, search online, research a topic using the web,
or asks for information that requires current web data:
{"action":"web_search","query":"<search query>"}

For any other request:
{"action":"general"}

Examples:

User: Create a 7 day study plan for Python
Output:
{"action":"study_plan","topic":"Python","days":7}

User: I need a 5 day study plan for mathematics
Output:
{"action":"study_plan","topic":"mathematics","days":5}

User: What are some good resources to learn Python?
Output:
{"action":"learning_resources","topic":"Python"}

User: What is 25% of 800?
Output:
{"action":"calculator","expression":"25 / 100 * 800"}

User: Search the latest AI news
Output:
{"action":"web_search","query":"latest AI news"}

User: Search the web for recent developments in artificial intelligence
Output:
{"action":"web_search","query":"recent developments in artificial intelligence"}

User: What are the latest Python releases?
Output:
{"action":"web_search","query":"latest Python releases"}

User: Explain machine learning
Output:
{"action":"general"}

IMPORTANT:
- Replace <actual topic> with the topic requested by the user.
- For web searches, create a concise search query from the user's request.
- Do not always use Python.
- Do not explain your decision.
- Do not return Markdown.
- Return JSON only.
"""

        for attempt in range(2):

            try:

                decision_response = (
                    self.client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[
                            {
                                "role": "system",
                                "content": system_prompt
                            },
                            {
                                "role": "user",
                                "content": user_input
                            }
                        ],
                        temperature=0,
                        max_tokens=150,
                        response_format={
                            "type": "json_object"
                        }
                    )
                )

                message = (
                    decision_response
                    .choices[0]
                    .message
                )

                ai_text = (
                    message.content or ""
                ).strip()

                if not ai_text:
                    continue

                decision = json.loads(
                    ai_text
                )

                if (
                    isinstance(decision, dict)
                    and decision.get("action")
                ):
                    return decision

            except Exception:
                continue

        return None

    def build_tool_response(
        self,
        user_input: str,
        action: str,
        tool_result
    ):

        response = (
            self.client.chat.completions.create(
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
                max_tokens=500,
                response_format={
                    "type": "json_object"
                },
            )
        )

        return {
            "status": "success",
            "agent": self.name,
            "action": action,
            "tool_result": tool_result,
            "response": (
                response
                .choices[0]
                .message
                .content
            )
        }

    def general_response(self, user_input: str):

        response = (
            self.client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are EduAgent AI, an "
                            "educational AI assistant. "
                            "Give concise, clear and "
                            "helpful answers. "
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
                response_format={
                    "type": "json_object"
                },
            )
        )

        return {
            "status": "success",
            "agent": self.name,
            "action": "general",
            "response": (
                response
                .choices[0]
                .message
                .content
            )
            }
