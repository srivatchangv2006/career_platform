def classify_ai_error(exc: Exception) -> str:
    """
    Convert AI failures into safe product-level statuses.

    The raw Gemini error is never exposed to the frontend.
    """

    status_code = getattr(exc, "status_code", None)

    if status_code == 429:
        return "RATE_LIMITED"

    error_code = getattr(exc, "code", None)

    if error_code == 429:
        return "RATE_LIMITED"

    message = str(exc).lower()

    if (
        "429" in message
        or "resource_exhausted" in message
        or "quota exceeded" in message
    ):
        return "RATE_LIMITED"

    return "UNAVAILABLE"
