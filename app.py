from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from agent import EduAgent


app = FastAPI(
    title="EduAgent AI - Amazon",
    description="Agentic AI learning assistant for the Amazon Developer Hackathon.",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://eduagent-amazon.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


agent = EduAgent()


class AgentRequest(BaseModel):
    user_input: str


class GroqRequest(BaseModel):
    message: str


def normalize_result(result):
    """
    Convert the agent result into a frontend-friendly response.
    """

    normalized = dict(result)

    tool_result = result.get("tool_result")

    if isinstance(tool_result, dict):
        if "message" in tool_result:
            normalized["message"] = tool_result["message"]

        if "result" in tool_result:
            normalized["result"] = tool_result["result"]

        if "resources" in tool_result:
            normalized["resources"] = tool_result["resources"]

        if "topic" in tool_result:
            normalized["topic"] = tool_result["topic"]

        if "days" in tool_result:
            normalized["days"] = tool_result["days"]

        if "expression" in tool_result:
            normalized["expression"] = tool_result["expression"]

    return normalized


@app.get("/")
def root():
    return {
        "status": "success",
        "message": "EduAgent AI - Amazon is running."
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/agent")
def run_agent(request: AgentRequest):
    result = agent.process(request.user_input)

    return normalize_result(result)


@app.post("/groq-test")
def groq_test(request: GroqRequest):
    response = agent.client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are EduAgent AI, an educational AI assistant. "
                    "Give concise, helpful answers."
                )
            },
            {
                "role": "user",
                "content": request.message
            }
        ],
        temperature=0.2,
        max_tokens=300
    )

    return {
        "status": "success",
        "response": response.choices[0].message.content
    }


@app.post("/alexa-simulate")
def alexa_simulate(request: AgentRequest):
    result = agent.process(request.user_input)

    return {
        "status": "success",
        "experience": "Alexa+ simulated experience",
        "user_input": request.user_input,
        "agent_result": normalize_result(result)
    }
