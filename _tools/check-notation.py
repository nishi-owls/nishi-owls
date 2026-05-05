#!/usr/bin/env python3
"""
Check for notation inconsistencies (表記ゆれ) in content files.

Rules are defined in _tools/notation-rules.yml:
  text_rules — check Japanese text in file content (full file including frontmatter)

Usage:
    python3 _tools/check-notation.py
"""

import os
import sys
import yaml
from pathlib import Path


def load_rules(rules_file):
    with open(rules_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_text_rules(file_path, content, rules):
    violations = []
    lines = content.splitlines()
    for rule in rules:
        expected = rule["expected"]
        for pattern in rule.get("patterns", []):
            for lineno, line in enumerate(lines, 1):
                if pattern in line:
                    violations.append(
                        {
                            "file": file_path,
                            "line": lineno,
                            "found": pattern,
                            "expected": expected,
                            "context": line.strip(),
                        }
                    )
    return violations


def main():
    repo_root = Path(__file__).parent.parent
    rules_file = Path(__file__).parent / "notation-rules.yml"

    if not rules_file.exists():
        print(f"Error: rules file not found at {rules_file}", file=sys.stderr)
        sys.exit(1)

    rules = load_rules(rules_file)
    text_rules = rules.get("text_rules", [])

    # Directories and file extensions to scan
    scan_dirs = ["_posts", "_games", "_data"]
    extensions = {".md", ".html", ".yml", ".yaml", ".csv"}

    all_violations = []
    file_count = 0

    for dir_name in scan_dirs:
        scan_dir = repo_root / dir_name
        if not scan_dir.exists():
            continue
        for file_path in sorted(scan_dir.rglob("*")):
            if not file_path.is_file() or file_path.suffix not in extensions:
                continue

            file_count += 1
            content = file_path.read_text(encoding="utf-8")

            if text_rules:
                all_violations.extend(check_text_rules(file_path, content, text_rules))

    print(f"Checked {file_count} files.\n")

    if not all_violations:
        print("✓ No notation inconsistencies found!")
        return 0

    print(f"✗ Found {len(all_violations)} issue(s):\n")
    for v in all_violations:
        rel_path = os.path.relpath(v["file"], repo_root)
        print(f"  {rel_path}:{v['line']}")
        print(f"    Found:    {v['found']}")
        print(f"    Expected: {v['expected']}")
        print(f"    Context:  {v['context'][:100]}")
        print()

    return 1


if __name__ == "__main__":
    sys.exit(main())
