def canonical_team_name(name: str) -> str:
    return " ".join(name.strip().split()).casefold()
