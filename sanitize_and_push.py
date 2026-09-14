#!/usr/bin/env python3
"""Sanitize scoreboard data.json and push to GitHub for Vercel deployment."""
import json
import subprocess
import sys
from pathlib import Path

SOURCE_DATA = Path('/mnt/workspace/scoreboard/data.json')
REPO_DIR = Path('/mnt/workspace/scoreboard-view')
TARGET_DATA = REPO_DIR / 'data.json'

# Fields to remove from each submission
SUBMISSION_FIELDS_TO_DROP = {
    'source',           # kernel.asc source code
    'account_id',       # team member account ID
    'user_id',          # team member user ID
}

# Top-level fields to drop from data.json
TOP_LEVEL_FIELDS_TO_DROP = {
    'pending_submissions',  # in-flight submission IDs
    'account_quotas',       # per-account quota tracking
}

def sanitize(data):
    """Remove sensitive fields from data."""
    # Drop top-level fields
    for field in TOP_LEVEL_FIELDS_TO_DROP:
        data.pop(field, None)
    
    # Drop fields from each submission
    for sub in data.get('submissions', []):
        for field in SUBMISSION_FIELDS_TO_DROP:
            sub.pop(field, None)
    
    return data

def main():
    if not SOURCE_DATA.exists():
        print(f'Error: {SOURCE_DATA} not found', file=sys.stderr)
        sys.exit(1)
    
    # Load and sanitize
    with open(SOURCE_DATA, 'r') as f:
        data = json.load(f)
    
    data = sanitize(data)
    
    # Write to repo
    with open(TARGET_DATA, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Git operations
    subprocess.run(['git', 'add', 'data.json'], cwd=REPO_DIR, check=True)
    
    # Check if there are changes
    result = subprocess.run(
        ['git', 'diff', '--quiet', '--cached', 'data.json'],
        cwd=REPO_DIR
    )
    
    if result.returncode == 0:
        print('No changes to push')
        return
    
    # Commit and push
    msg = f"Update data ({len(data.get('submissions', []))} submissions)"
    subprocess.run(['git', 'commit', '-m', msg], cwd=REPO_DIR, check=True)
    subprocess.run(['git', 'push'], cwd=REPO_DIR, check=True)
    print('Pushed to GitHub')

if __name__ == '__main__':
    main()
