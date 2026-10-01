from fastapi import FastAPI

app = FastAPI(
    title="EduAgent AI - Amazon",
    description="Agentic AI learning assistant for the Amazon Developer Hackathon.",
    version="1.0.0"
)


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
