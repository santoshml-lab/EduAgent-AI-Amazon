from groq import Groq
import os
import json
import re

from tools_registry import create_tool_manager


class EduAgent:

    MAX_TOOL_STEPS = 4

    ALLOWED_TOOLS = {
        "study_plan",
        "learning_resources",
        "calculator",
        "web_search"
    }

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

        mode = decision.get("mode", "single_tool")

        trace.append({
            "step": 2,
            "stage": "intent_detection",
            "message": f"Execution mode detected: {mode}."
        })

        if mode == "multi_tool":
            return self.process_multi_tool(
                user_input,
                decision,
                trace
            )

        action = decision.get("action")

        trace.append({
            "step": 3,
            "stage": "tool_selection",
            "message": f"Selected action: {action}."
        })

        if action == "study_plan":
            return self.execute_single_tool(
                user_input,
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
                },
                trace
            )

        if action == "learning_resources":
            return self.execute_single_tool(
                user_input,
                "learning_resources",
                {
                    "topic": decision.get(
                        "topic",
                        "General"
                    )
                },
                trace
            )

        if action == "calculator":
            return self.execute_single_tool(
                user_input,
                "calculator",
                {
                    "expression": decision.get(
                        "expression",
                        ""
                    )
                },
                trace
            )

        if action == "web_search":
            return self.execute_single_tool(
                user_input,
                "web_search",
                {
                    "query": decision.get(
                        "query",
                        user_input
                    )
                },
                trace
            )

        if action == "general":
            trace.append({
                "step": 4,
                "stage": "reasoning",
                "message": "General educational response selected."
            })

            result = self.general_response(
                user_input
            )

            result["trace"] = trace + [
                {
                    "step": 5,
                    "stage": "response",
                    "message": "AI response generated."
                }
            ]

            return result

        trace.append({
            "step": 4,
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
You are the planning brain of EduAgent AI.

Your job is to decide whether the user request needs:
1. one tool,
2. multiple tools,
3. or a normal educational AI response.

Available tools:

- study_plan
- learning_resources
- calculator
- web_search

Return ONLY valid JSON.
Do not return Markdown.
Do not explain the decision.

For ONE tool use:

{
  "mode": "single_tool",
  "action": "study_plan",
  "topic": "Python",
  "days": 7
}

For MULTIPLE tools use:

{
  "mode": "multi_tool",
  "steps": [
    {
      "tool": "study_plan",
      "arguments": {
        "topic": "mathematics",
        "days": 7
      }
    },
    {
      "tool": "learning_resources",
      "arguments": {
        "topic": "mathematics"
      }
    }
  ]
}

For a normal response use:

{
  "mode": "general",
  "action": "general"
}

Rules:

- Use study_plan when the user asks for a study schedule or study plan.
- Use learning_resources when the user asks for resources, materials, practice resources, or learning guidance.
- Use calculator for mathematical calculations.
- Use web_search when the user explicitly asks to search online, asks for latest/current information, recent news, or information that requires current web data.
- Use multiple tools when the request clearly requires more than one independent action.
- Use no more than 4 tools.
- Never invent a tool name.
- Never include tools outside the available tool list.
- Preserve the actual topic from the user.
- If the user gives a number of days, preserve it.
- If a study plan is requested but no number of days is provided, use 7 days.
- For calculator, provide the mathematical expression only.
- For web search, create a concise search query.
- If the request can be answered normally without a tool, use general.

Examples:

User:
Create a 7 day study plan for Python

Output:
{
  "mode": "single_tool",
  "action": "study_plan",
  "topic": "Python",
  "days": 7
}

User:
Give me resources to learn Python

Output:
{
  "mode": "single_tool",
  "action": "learning_resources",
  "topic": "Python"
}

User:
Calculate 125 * 48

Output:
{
  "mode": "single_tool",
  "action": "calculator",
  "expression": "125 * 48"
}

User:
Search the latest AI news

Output:
{
  "mode": "single_tool",
  "action": "web_search",
  "query": "latest AI news"
}

User:
I have a mathematics exam in 7 days. Create a study plan and give me learning resources.

Output:
{
  "mode": "multi_tool",
  "steps": [
    {
      "tool": "study_plan",
      "arguments": {
        "topic": "mathematics",
        "days": 7
      }
    },
    {
      "tool": "learning_resources",
      "arguments": {
        "topic": "mathematics"
      }
    }
  ]
}

User:
Calculate 25 * 40 and search the latest AI news.

Output:
{
  "mode": "multi_tool",
  "steps": [
    {
      "tool": "calculator",
      "arguments": {
        "expression": "25 * 40"
      }
    },
    {
      "tool": "web_search",
      "arguments": {
        "query": "latest AI news"
      }
    }
  ]
}

User:
Explain machine learning.

Output:
{
  "mode": "general",
  "action": "general"
}
"""

        for attempt in range(2):

            try:

                response = (
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
                        max_tokens=400
                    )
                )

                ai_text = (
                    response
                    .choices[0]
                    .message
                    .content or ""
                ).strip()

                decision = self.parse_json_response(
                    ai_text
                )

                if self.validate_decision(
                    decision
                ):
                    return decision

            except Exception:
                continue

        return None

    def parse_json_response(self, text: str):

        if not text:
            return None

        cleaned = text.strip()

        if cleaned.startswith("```"):
            cleaned = re.sub(
                r"^```(?:json)?\s*",
                "",
                cleaned,
                flags=re.IGNORECASE
            )

            cleaned = re.sub(
                r"\s*```$",
                "",
                cleaned
            )

        try:
            return json.loads(cleaned)

        except json.JSONDecodeError:

            match = re.search(
                r"\{.*\}",
                cleaned,
                flags=re.DOTALL
            )

            if not match:
                return None

            try:
                return json.loads(
                    match.group(0)
                )
            except json.JSONDecodeError:
                return None

    def validate_decision(self, decision):

        if not isinstance(
            decision,
            dict
        ):
            return False

        mode = decision.get(
            "mode"
        )

        if mode == "general":
            return (
                decision.get("action")
                == "general"
            )

        if mode == "single_tool":

            action = decision.get(
                "action"
            )

            if action not in self.ALLOWED_TOOLS:
                return False

            return True

        if mode == "multi_tool":

            steps = decision.get(
                "steps"
            )

            if not isinstance(
                steps,
                list
            ):
                return False

            if not steps:
                return False

            if len(steps) > self.MAX_TOOL_STEPS:
                return False

            for step in steps:

                if not isinstance(
                    step,
                    dict
                ):
                    return False

                tool_name = step.get(
                    "tool"
                )

                if tool_name not in self.ALLOWED_TOOLS:
                    return False

                arguments = step.get(
                    "arguments",
                    {}
                )

                if not isinstance(
                    arguments,
                    dict
                ):
                    return False

            return True

        return False

    def execute_single_tool(
        self,
        user_input,
        action,
        arguments,
        trace
    ):

        try:

            tool_result = (
                self.tool_manager.execute_tool(
                    action,
                    arguments
                )
            )

            trace.append({
                "step": 4,
                "stage": "tool_execution",
                "message": (
                    f"{action} executed successfully."
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

        except Exception as error:

            trace.append({
                "step": 4,
                "stage": "tool_execution",
                "message": (
                    f"{action} execution failed."
                )
            })

            return {
                "status": "error",
                "agent": self.name,
                "action": action,
                "message": "Tool execution failed.",
                "error": str(error),
                "trace": trace
            }

    def process_multi_tool(
        self,
        user_input,
        decision,
        trace
    ):

        steps = decision.get(
            "steps",
            []
        )

        trace.append({
            "step": 3,
            "stage": "planning",
            "message": (
                f"Planner created {len(steps)} tool steps."
            )
        })

        tool_results = []

        for index, step in enumerate(
            steps,
            start=1
        ):

            tool_name = step.get(
                "tool"
            )

            arguments = step.get(
                "arguments",
                {}
            )

            if tool_name not in self.ALLOWED_TOOLS:

                trace.append({
                    "step": 3 + index,
                    "stage": "validation",
                    "message": (
                        f"Blocked unsupported tool: "
                        f"{tool_name}."
                    )
                })

                continue

            trace.append({
                "step": 3 + index,
                "stage": "tool_selection",
                "message": (
                    f"Tool {index} selected: "
                    f"{tool_name}."
                )
            })

            try:

                result = (
                    self.tool_manager.execute_tool(
                        tool_name,
                        arguments
                    )
                )

                tool_results.append({
                    "tool": tool_name,
                    "arguments": arguments,
                    "result": result
                })

                trace.append({
                    "step": 3 + index,
                    "stage": "tool_execution",
                    "message": (
                        f"{tool_name} executed successfully."
                    )
                })

            except Exception as error:

                tool_results.append({
                    "tool": tool_name,
                    "arguments": arguments,
                    "result": {
                        "error": str(error)
                    }
                })

                trace.append({
                    "step": 3 + index,
                    "stage": "tool_execution",
                    "message": (
                        f"{tool_name} execution failed."
                    )
                })

        if not tool_results:

            return {
                "status": "error",
                "agent": self.name,
                "action": "multi_tool",
                "message": "No tools were successfully executed.",
                "trace": trace
            }

        final_response = (
            self.build_multi_tool_response(
                user_input,
                tool_results
            )
        )

        trace.append({
            "step": 4 + len(steps),
            "stage": "aggregation",
            "message": (
                "Tool results aggregated."
            )
        })

        trace.append({
            "step": 5 + len(steps),
            "stage": "response",
            "message": (
                "Final multi-tool response generated."
            )
        })

        final_response["trace"] = trace

        return final_response

    def build_multi_tool_response(
        self,
        user_input,
        tool_results
    ):

        try:

            response = (
                self.client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are EduAgent AI. "
                                "Combine the results of multiple "
                                "educational tools into one concise "
                                "natural response. "
                                "Do not invent information. "
                                "Use only the supplied tool results. "
                                "Explain what was completed."
                            )
                        },
                        {
                            "role": "user",
                            "content": json.dumps({
                                "user_request": user_input,
                                "tool_results": tool_results
                            })
                        }
                    ],
                    temperature=0.1,
                    max_tokens=500
                )
            )

            final_text = (
                response
                .choices[0]
                .message
                .content or ""
            ).strip()

            return {
                "status": "success",
                "agent": self.name,
                "action": "multi_tool",
                "tool_results": tool_results,
                "response": final_text
            }

        except Exception as error:

            return {
                "status": "success",
                "agent": self.name,
                "action": "multi_tool",
                "tool_results": tool_results,
                "response": (
                    "The requested tools were executed "
                    "successfully, but the final response "
                    "could not be generated."
                ),
                "error": str(error)
            }

    def build_tool_response(
        self,
        user_input: str,
        action: str,
        tool_result
    ):

        if action == "web_search":

            if (
                isinstance(tool_result, dict)
                and tool_result.get("error")
            ):

                return {
                    "status": "error",
                    "agent": self.name,
                    "action": action,
                    "tool_result": tool_result,
                    "response": json.dumps({
                        "summary": tool_result.get(
                            "error",
                            "Web search failed."
                        )
                    })
                }

            if isinstance(
                tool_result,
                dict
            ):

                answer = tool_result.get(
                    "answer"
                )

                if answer:

                    summary = answer

                else:

                    results = tool_result.get(
                        "results",
                        []
                    )

                    if results:

                        summary = (
                            "Web search returned "
                            f"{len(results)} relevant results."
                        )

                    else:

                        summary = (
                            "The web search did not return "
                            "enough information."
                        )

                return {
                    "status": "success",
                    "agent": self.name,
                    "action": action,
                    "tool_result": tool_result,
                    "response": json.dumps({
                        "summary": summary
                    })
                }

        system_prompt = """
You are EduAgent AI.

You have just executed an educational tool.

Use the tool result to answer the user's request naturally.

Rules:
- Be concise and helpful.
- Do not mention internal implementation details.
- Do not invent information.
- Use only information available in the tool result.
- Return valid JSON only.

Use this structure:

{
  "summary": "natural concise response"
}
"""

        try:

            response = (
                self.client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
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
                    temperature=0,
                    max_tokens=500
                )
            )

            content = (
                response
                .choices[0]
                .message
                .content or ""
            ).strip()

            return {
                "status": "success",
                "agent": self.name,
                "action": action,
                "tool_result": tool_result,
                "response": content
            }

        except Exception as error:

            return {
                "status": "success",
                "agent": self.name,
                "action": action,
                "tool_result": tool_result,
                "response": json.dumps({
                    "summary": (
                        "The tool executed successfully."
                    ),
                    "error": str(error)
                })
            }

    def general_response(
        self,
        user_input: str
    ):

        try:

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
                                "helpful answers."
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
            )

            return {
                "status": "success",
                "agent": self.name,
                "action": "general",
                "response": (
                    response
                    .choices[0]
                    .message
                    .content or ""
                ).strip()
            }

        except Exception as error:

            return {
                "status": "error",
                "agent": self.name,
                "action": "general",
                "response": json.dumps({
                    "summary": (
                        "The AI response could not be generated."
                    ),
                    "error": str(error)
                })
                    }

