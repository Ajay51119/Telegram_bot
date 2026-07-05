"""Builds the human-readable resume-extraction confirmation message."""

from resume.parser import ExtractedResumeProfile


def _field_line(label: str, emoji: str, new_value, old_value) -> str:
    if new_value:
        if old_value and old_value != new_value:
            suffix = f" _(was: {old_value})_"
        elif not old_value:
            suffix = " 💡 _(wasn't set yet — recommended)_"
        else:
            suffix = ""
        return f"{emoji} {label}: *{new_value}*{suffix}"
    return f"{emoji} {label}: _not found in resume_"


def build_confirmation_text(extracted: ExtractedResumeProfile, existing_user: dict) -> str:
    existing_user = existing_user or {}
    lines = ["📋 Here's what I found in your resume:\n"]
    lines.append(_field_line("Name", "🙋", extracted.name, existing_user.get("username")))
    lines.append(_field_line("Email", "📧", extracted.email, existing_user.get("email")))
    lines.append(_field_line("Profile", "🧩", extracted.profile, existing_user.get("profile")))
    lines.append(
        _field_line("Looking for", "🎯", extracted.designation, existing_user.get("designation"))
    )
    if extracted.skills:
        lines.append(f"\n🛠️ Skills: {', '.join(extracted.skills)}")
    lines.append("\nAllow me to update your profile with this?")
    return "\n".join(lines)
