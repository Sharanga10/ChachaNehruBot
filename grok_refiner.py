def refine_with_grok(content: str) -> str:
    """
    Enhance or clean up Grok-generated content if needed.
    Currently a passthrough but can apply virality boosting, keyword shaping, etc.
    """
    if not content:
        return ""

    refined = content.strip()

    # Apply basic cleanup
    refined = refined.replace("...", "…").replace(" ,", ",")

    # Future: Apply custom tone shaping, Hashtag alignment, etc.
    return refined