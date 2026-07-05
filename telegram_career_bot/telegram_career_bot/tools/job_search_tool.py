"""
Dummy "current job openings" tool.

In a real deployment, swap the body of `search_jobs` to call a real job
board API (LinkedIn, Naukri, Indeed, an internal ATS, etc). For now it
reads from a static local JSON file so the agent works end-to-end with
zero external dependencies.
"""

import json
from pathlib import Path

from langchain_core.tools import tool

JOBS_FILE = Path(__file__).resolve().parent.parent / "data" / "jobs.json"


@tool
def search_jobs(query: str = "", location: str = "") -> str:
    """Search current job openings (demo dataset) by role/skill keyword and/or location.

    Args:
        query: A keyword to match against job title or required skills,
            e.g. "python developer", "data scientist", "react".
        location: A city or "remote" to filter by, e.g. "Hyderabad", "remote".
            Leave empty to search all locations.

    Returns:
        A formatted, human-readable string listing up to 5 matching jobs,
        or a message saying no matches were found.
    """
    with open(JOBS_FILE, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    q = query.strip().lower()
    loc = location.strip().lower()

    def matches(job: dict) -> bool:
        title_or_skill_match = True
        if q:
            title_or_skill_match = q in job["title"].lower() or any(
                q in skill.lower() for skill in job.get("skills", [])
            )
        location_match = True
        if loc:
            location_match = loc in job["location"].lower()
        return title_or_skill_match and location_match

    results = [job for job in jobs if matches(job)][:5]

    if not results:
        return (
            "No matching job listings found in the demo dataset. "
            "Try a broader keyword (e.g. just 'python' or 'developer') "
            "or drop the location filter."
        )

    lines = []
    for job in results:
        lines.append(
            f"🔹 *{job['title']}* — {job['company']}\n"
            f"   📍 {job['location']} | 💰 {job['salary']} | 🧩 {job['experience']}\n"
            f"   Skills: {', '.join(job['skills'])}\n"
            f"   🔗 {job['link']}"
        )
    return "\n\n".join(lines)
