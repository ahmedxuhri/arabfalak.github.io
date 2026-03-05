#!/usr/bin/env python3
"""
Check for slug conflicts before publishing a post
"""
import json
import sys
from pathlib import Path

def check_slug_conflict(slug, existing_slugs=None):
    """
    Check if a slug already exists in the system
    Returns: (is_conflict, message)
    """
    if existing_slugs is None:
        siteurls_file = Path('/root/arabfalak/data/siteurls.json')
        if siteurls_file.exists():
            try:
                with open(siteurls_file, 'r', encoding='utf-8') as f:
                    posts = json.load(f)
                existing_slugs = [post['slug'] for post in posts]
            except json.JSONDecodeError:
                return False, "Could not read siteurls.json"
        else:
            existing_slugs = []
    
    if slug in existing_slugs:
        return True, f"❌ Slug conflict: '{slug}' already exists!"
    
    # Also check if directory exists at root level
    post_path = Path('/root/arabfalak') / slug
    if post_path.exists():
        return True, f"❌ Directory conflict: /{slug}/ already exists!"
    
    return False, f"✅ Slug '{slug}' is available"

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: check_slug_conflict.py <slug>")
        sys.exit(1)
    
    slug = sys.argv[1]
    is_conflict, message = check_slug_conflict(slug)
    print(message)
    
    if is_conflict:
        sys.exit(1)
    sys.exit(0)
