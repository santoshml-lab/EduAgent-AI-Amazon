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

        # Study Plan
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
                "message": "Study Plan Tool executed successfully."
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

        # Learning Resources
        if action == "learning_resources":

            trace.append({
                "step": 3,
                "stage": "tool_selection",
                "message": "Learning Resources Tool selected."
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

        # Calculator
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
                "message": "Calculator Tool executed successfully."
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

        # Web Search
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

            if (
                isinstance(tool_result, dict)
                and tool_result.get("error")
            ):

                trace.append({
                    "step": 4,
                    "stage": "tool_execution",
                    "message": "Web Search Tool returned an error."
                })

            else:

                trace.append({
                    "step": 4,
                    "stage": "tool_execution",
                    "message": "Web Search Tool executed successfully."
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
                    "message": "Web search response completed."
                }
            ]

            return result

        # General AI
        if action == "general":

            trace.append({
                "step": 3,
                "stage": "reasoning",
                "message": "General educational response selected."
            })

            result = self

