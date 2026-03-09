from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="MCP Generic Webhook Example")


class EmailRequest(BaseModel):
    to: str
    subject: str


@app.post("/send-email")
async def send_email(payload: EmailRequest):
    print(f"Sending email to: {payload.to} with subject: {payload.subject}")
    return {"status": "success", "message": f"Email sent to {payload.to} successfully!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
