"""Detail-page extraction (starter implementation)."""


def fetch_detail(item: dict[str, str]) -> dict[str, str]:
    """
    Add placeholder detail fields for one listing item.

    Replace this with network/browser extraction in the next phase.
    """
    return {
        **item,
        "price": "N/A",
        "location": "Unknown",
        "description": f"Placeholder detail for {item['id']}",
    }
