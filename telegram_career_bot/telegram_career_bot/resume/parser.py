"""
Turns raw extracted resume text into structured fields using the same
get_structured_llm() helper the orchestrator uses — so it automatically
gets Groq/OpenRouter auto-fallback for free.
"""

from typing import List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from config import get_structured_llm
from resume.extractor import find_email_regex

PARSE_SYSTEM_PROMPT = """You are a resume parser. Extract structured fields from raw resume
text that may contain OCR noise/typos — be forgiving of formatting artifacts.

- name: the candidate's full name.
- email: their email address.
- profile: a short label for their current professional profile/domain,
  e.g. "Backend Developer", "Data Scientist", "Frontend Engineer". Infer this
  from their most recent role / summary, not a guess if genuinely unclear.
- designation: the single job title they appear to be targeting next — from an
  "objective"/"summary" section if present, otherwise infer from their most
  recent/senior role.
- skills: up to 12 concrete technical or professional skills as short keywords
  (e.g. "Python", "AWS", "React"), not full sentences.

If a field genuinely cannot be determined, leave it null (skills: empty list)."""


class ExtractedResumeProfile(BaseModel):
    name: Optional[str] = Field(None, description="Candidate's full name")
    email: Optional[str] = Field(None, description="Candidate's email address")
    profile: Optional[str] = Field(
        None, description="Short label for the candidate's current professional profile/domain"
    )
    designation: Optional[str] = Field(
        None, description="The single job title the candidate appears to be targeting next"
    )
    skills: List[str] = Field(
        default_factory=list, description="Up to 12 concrete skills found in the resume"
    )


def parse_resume_text(resume_text: str) -> ExtractedResumeProfile:
    llm = get_structured_llm(ExtractedResumeProfile, temperature=0.0)
    result: ExtractedResumeProfile = llm.invoke(
        [
            SystemMessage(content=PARSE_SYSTEM_PROMPT),
            # Guard against extremely long resumes blowing the context window.
            HumanMessage(content=resume_text[:8000]),
        ]
    )

    if not result.email:
        regex_email = find_email_regex(resume_text)
        if regex_email:
            result.email = regex_email

    return result
