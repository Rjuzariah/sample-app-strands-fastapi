from pathlib import Path


def needs_revision(state) -> bool:
    review_result = state.results.get("code_review")
    if review_result is None:
        return False
    return review_result.result.structured_output.review_status not in ("approved", "passed")


def load_prompt(filename):
    return Path(
        f"prompts/{filename}"
    ).read_text(encoding="utf-8")
