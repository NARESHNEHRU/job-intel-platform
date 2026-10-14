from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.agent.chat import answer

router = APIRouter(tags=["chat"])


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    job_id: str | None = None            # the job the user is pointing at, if any
    last_job_ids: list[str] = []         # jobs shown in the previous answer


@router.post("/chat")
def chat(body: ChatIn):
    return answer(body.message.strip(), body.job_id, body.last_job_ids[:20])