#!/usr/bin/env python3
"""
Check game file frontmatter against known opponents and venues.

For each game file in _games/, verifies that:
  - vs       is a known short name
  - vs_full  matches the known full name(s) for that vs
  - filename contains one of the known slugs for that vs
  - place    is a known venue

Also checks _data/next-games.yml for valid vs and place values.
Placeholder values (未定, 場所未定, (opponent TBD), etc.) are skipped.

Rules are defined in _tools/known-names.yml.
When adding a new opponent or venue, update that file in the same commit.

Usage:
    python3 _tools/check-names.py
"""

import os
import re
import sys
import yaml
from pathlib import Path


def load_known(names_file):
    with open(names_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    teams = {}
    for entry in data.get("teams", []):
        vs = entry["vs"]
        vs_full = entry.get("vs_full", [])
        if isinstance(vs_full, str):
            vs_full = [vs_full]
        teams[vs] = {
            "vs_full": set(vs_full),
            "vs_full_pattern": entry.get("vs_full_pattern"),
            "slug": entry.get("slug", ""),
        }

    places = set(data.get("places", []))
    return teams, places


def extract_frontmatter(file_path):
    content = file_path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    try:
        return yaml.safe_load(content[4:end])
    except yaml.YAMLError as e:
        print(f"Error parsing YAML in {file_path}: {e}", file=sys.stderr)
        return None


def extract_slug(stem):
    # Normalize full-width hyphens (U+2212) to ASCII hyphens, then strip date prefix
    normalized = stem.replace("−", "-")
    return re.sub(r"^\d{4}-\d{1,2}-\d{1,2}-", "", normalized)


def check_game_file(file_path, teams, places, repo_root):
    fm = extract_frontmatter(file_path)
    if fm is None:
        return []

    vs = fm.get("vs")
    vs_full = fm.get("vs_full")
    place = fm.get("place")
    slug = extract_slug(file_path.stem)
    rel = os.path.relpath(file_path, repo_root)

    issues = []

    # vs
    if vs is None:
        issues.append(f"{rel}: missing 'vs' field")
        return issues

    if not isinstance(vs, str):
        issues.append(f"{rel}: vs must be a string, got {type(vs).__name__}")
        return issues

    if vs not in teams:
        issues.append(f"{rel}: unknown vs '{vs}' — add to known-names.yml")
        return issues

    entry = teams[vs]

    # vs_full
    if vs_full is None:
        issues.append(f"{rel}: missing 'vs_full' field")
    elif not isinstance(vs_full, str):
        issues.append(f"{rel}: vs_full must be a string, got {type(vs_full).__name__}")
    elif pattern := entry["vs_full_pattern"]:
        if not re.fullmatch(pattern, vs_full):
            issues.append(f"{rel}: vs_full '{vs_full}' does not match pattern '{pattern}' for '{vs}'")
    elif vs_full not in entry["vs_full"]:
        valid = ", ".join(f"'{v}'" for v in sorted(entry["vs_full"]))
        issues.append(f"{rel}: vs_full '{vs_full}' not in known values for '{vs}': {valid}")

    # slug
    if slug != entry["slug"]:
        issues.append(f"{rel}: filename slug '{slug}' should be '{entry['slug']}'")

    # place
    if place is None:
        issues.append(f"{rel}: missing 'place' field")
    elif not isinstance(place, str):
        issues.append(f"{rel}: place must be a string, got {type(place).__name__}")
    elif place not in places:
        issues.append(f"{rel}: unknown place '{place}' — add to known-names.yml")

    return issues


def is_placeholder(value):
    """Return True for undecided/TBD values that should skip validation."""
    if value is None:
        return False
    s = str(value)
    return s.startswith("(") or "未定" in s or "未公開" in s


def check_next_games(file_path, teams, places, repo_root):
    with open(file_path, "r", encoding="utf-8") as f:
        entries = yaml.safe_load(f)
    if not entries:
        return []

    rel = os.path.relpath(file_path, repo_root)
    issues = []

    for i, entry in enumerate(entries):
        loc = f"{rel}[{i}]"
        vs = entry.get("vs")
        place = entry.get("place")

        if vs is None:
            issues.append(f"{loc}: missing 'vs' field")
        elif not isinstance(vs, str):
            issues.append(f"{loc}: vs must be a string, got {type(vs).__name__}")
        elif not is_placeholder(vs) and vs not in teams:
            issues.append(f"{loc}: unknown vs '{vs}' — add to known-names.yml")

        if place is None:
            issues.append(f"{loc}: missing 'place' field")
        elif not isinstance(place, str):
            issues.append(f"{loc}: place must be a string, got {type(place).__name__}")
        elif not is_placeholder(place) and place not in places:
            issues.append(f"{loc}: unknown place '{place}' — add to known-names.yml")

    return issues


def main():
    repo_root = Path(__file__).parent.parent
    names_file = Path(__file__).parent / "known-names.yml"

    if not names_file.exists():
        print(f"Error: {names_file} not found", file=sys.stderr)
        sys.exit(1)

    teams, places = load_known(names_file)
    games_dir = repo_root / "_games"

    all_issues = []
    file_count = 0

    for f in sorted(games_dir.rglob("*.html")):
        file_count += 1
        all_issues.extend(check_game_file(f, teams, places, repo_root))

    next_games_file = repo_root / "_data" / "next-games.yml"
    if next_games_file.exists():
        file_count += 1
        all_issues.extend(check_next_games(next_games_file, teams, places, repo_root))

    print(f"Checked {file_count} files.\n")

    if not all_issues:
        print("✓ All files passed name/venue checks!")
        return 0

    print(f"✗ Found {len(all_issues)} issue(s):\n")
    for issue in all_issues:
        print(f"  {issue}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
