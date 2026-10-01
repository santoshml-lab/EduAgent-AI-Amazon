from fastapi import FastAPI
from pydantic import BaseModel

from agent import EduAgent

app = FastAPI(
    title="EduAgent AI - Amazon",
    description="Agentic AI learning assistant for the Amazon Developer Hackathon.",
    version="1.0.0"
)

agent = EduAgent()


class AgentRequest(BaseModel):
    user_input: str


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

    return result
