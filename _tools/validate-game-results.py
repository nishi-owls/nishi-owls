#!/usr/bin/env python3
"""
Validate game results consistency.

This script checks that the 'result' field in game files matches the actual scores:
- result: win => our_score > vs_score (or tied with tiebreaker)
- result: lose => our_score < vs_score (or tied with tiebreaker)
- result: tie => our_score == vs_score

Also checks for:
- Field name typos (e.g., 'out_scores' instead of 'our_scores')
- Missing required fields (result, our_score, vs_score)
- Score sum validation: sum(our_scores) == our_score and sum(vs_scores) == vs_score

Usage:
    python3 _tools/validate-game-results.py
"""

import os
import sys
import yaml
from pathlib import Path

def extract_frontmatter(file_path):
    """Extract YAML frontmatter from a Jekyll file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        return None

    # Find the second '---'
    end_idx = content.find('---', 3)
    if end_idx == -1:
        return None

    frontmatter_str = content[4:end_idx]
    try:
        return yaml.safe_load(frontmatter_str)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML in {file_path}: {e}", file=sys.stderr)
        return None

def validate_game_file(file_path):
    """Validate a single game file."""
    frontmatter = extract_frontmatter(file_path)
    if not frontmatter:
        return None

    # Check if required fields exist
    result = frontmatter.get('result')
    our_score = frontmatter.get('our_score')
    vs_score = frontmatter.get('vs_score')

    # Skip if any required field is missing
    if result is None or our_score is None or vs_score is None:
        return {
            'file': file_path,
            'error': 'missing_fields',
            'details': f"Missing required fields (result={result}, our_score={our_score}, vs_score={vs_score})"
        }

    # Check for typos in field names
    issues = []
    if 'out_scores' in frontmatter:
        issues.append("Found 'out_scores' (should be 'our_scores')")

    # Validate score sums
    our_scores = frontmatter.get('our_scores', [])
    vs_scores = frontmatter.get('vs_scores', [])

    # Calculate sum of scores (excluding non-numeric values like '○' for tiebreakers)
    if our_scores:
        our_scores_sum = sum(s for s in our_scores if isinstance(s, (int, float)))
        if our_scores_sum != our_score:
            issues.append(f"Score sum mismatch: sum(our_scores) = {our_scores_sum} but our_score = {our_score}")

    if vs_scores:
        vs_scores_sum = sum(s for s in vs_scores if isinstance(s, (int, float)))
        if vs_scores_sum != vs_score:
            issues.append(f"Score sum mismatch: sum(vs_scores) = {vs_scores_sum} but vs_score = {vs_score}")

    # Validate result against scores - only catch contradictions
    # result='win' but our_score < vs_score => ERROR
    # result='lose' but our_score > vs_score => ERROR
    # result='tie' but scores don't match => ERROR
    # For tied scores, 'win' and 'lose' are allowed (tiebreaker games)

    if result == 'win' and our_score < vs_score:
        issues.append(f"Result contradiction: result='win' but our_score < vs_score ({our_score} < {vs_score})")
    elif result == 'lose' and our_score > vs_score:
        issues.append(f"Result contradiction: result='lose' but our_score > vs_score ({our_score} > {vs_score})")
    elif result == 'tie' and our_score != vs_score:
        issues.append(f"Result contradiction: result='tie' but scores don't match ({our_score} ≠ {vs_score})")

    if issues:
        return {
            'file': file_path,
            'error': 'validation_failed',
            'details': '; '.join(issues),
            'frontmatter': {
                'result': result,
                'our_score': our_score,
                'vs_score': vs_score
            }
        }

    return None

def main():
    # Find all game files
    repo_root = Path(__file__).parent.parent
    games_dir = repo_root / '_games'

    if not games_dir.exists():
        print(f"Error: Games directory not found at {games_dir}", file=sys.stderr)
        sys.exit(1)

    game_files = list(games_dir.glob('**/*.html'))

    print(f"Checking {len(game_files)} game files...\n")

    errors = []
    for game_file in sorted(game_files):
        error = validate_game_file(game_file)
        if error:
            errors.append(error)

    # Print results
    if not errors:
        print("✓ All game files passed validation!")
        return 0

    print(f"✗ Found {len(errors)} issue(s):\n")
    for error in errors:
        rel_path = os.path.relpath(error['file'], repo_root)
        print(f"File: {rel_path}")
        print(f"  Error: {error['error']}")
        print(f"  Details: {error['details']}")
        if 'frontmatter' in error:
            fm = error['frontmatter']
            print(f"  Current values: result='{fm['result']}', our_score={fm['our_score']}, vs_score={fm['vs_score']}")
        print()

    return 1

if __name__ == '__main__':
    sys.exit(main())
