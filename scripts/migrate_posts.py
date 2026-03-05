#!/usr/bin/env python3
"""
Migrate existing posts from /posts/{slug}/ to /{slug}/
This script should only be run once
"""
import shutil
import json
from pathlib import Path

def migrate_posts():
    """Move post directories from /posts/ to root level"""
    posts_dir = Path('/root/arabfalak/posts')
    root_dir = Path('/root/arabfalak')
    
    if not posts_dir.exists():
        print("No /posts/ directory found - nothing to migrate")
        return
    
    migrated = []
    skipped = []
    
    # Get list of existing posts from siteurls.json
    siteurls_file = Path('/root/arabfalak/data/siteurls.json')
    if siteurls_file.exists():
        with open(siteurls_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)
        slugs = {post['slug'] for post in posts}
    else:
        slugs = set()
    
    # Migrate each post directory
    for post_dir in posts_dir.iterdir():
        if not post_dir.is_dir():
            continue
        
        slug = post_dir.name
        target_dir = root_dir / slug
        
        if slug not in slugs:
            print(f"⏭️  Skipping {slug} - not in siteurls.json")
            skipped.append(slug)
            continue
        
        if target_dir.exists() and target_dir != post_dir:
            print(f"⚠️  {slug} already exists at root level - skipping")
            skipped.append(slug)
            continue
        
        # Move directory
        if target_dir.exists():
            shutil.rmtree(target_dir)
        
        shutil.move(str(post_dir), str(target_dir))
        print(f"✅ Migrated: {slug}")
        migrated.append(slug)
    
    # Remove empty /posts/ directory
    if not any(posts_dir.iterdir()):
        posts_dir.rmdir()
        print("✅ Removed empty /posts/ directory")
    
    print(f"\n📊 Migration summary:")
    print(f"   ✅ Migrated: {len(migrated)}")
    print(f"   ⏭️  Skipped: {len(skipped)}")
    
    return len(migrated) > 0

if __name__ == '__main__':
    migrate_posts()
