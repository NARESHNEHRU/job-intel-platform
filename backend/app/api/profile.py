from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from backend.app.services.degrees import find_degrees
from backend.app.services.profile import load_profile, save_profile
from backend.app.services.resume import extract_skills, read_resume_text


router = APIRouter(
    prefix="/profile",
    tags=["profile"],
)


class ProfileIn(BaseModel):
    name: str = ""
    skills: list[str] = []
    experience_years: float = Field(0, ge=0, le=40)
    education: str = ""
    preferred_roles: str = ""
    preferred_locations: list[str] = []
    min_salary_lpa: float | None = Field(None, ge=0)
    work_mode: str | None = None


@router.get("")
def get_profile():
    return load_profile()


@router.put("")
def put_profile(profile: ProfileIn):
    return save_profile(profile.model_dump())


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...)
):
    data = await file.read()

    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(
            413,
            "File too large (max 5 MB)"
        )

    try:
        text = read_resume_text(
            file.filename or "",
            data
        )

    except ValueError as error:
        raise HTTPException(
            400,
            str(error)
        )

    except Exception:
        raise HTTPException(
            400,
            "Could not read this file"
        )

    if len(text.strip()) < 50:
        raise HTTPException(
            422,
            "No readable text found. Is this a scanned image PDF?"
        )

    return {
        "skills": extract_skills(text),
        "education": ", ".join(
            sorted(find_degrees(text))
        ),
        "characters_read": len(text),
    }