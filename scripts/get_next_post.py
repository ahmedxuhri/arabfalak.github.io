#!/usr/bin/env python3
"""
Get the next post to generate from the future-posts.json queue
"""
import json
import sys
from pathlib import Path

def get_next_post():
    """
    Get the next pending post from the queue.
    Returns: (title, category) tuple or None
    """
    future_posts_file = Path('/root/arabfalak/data/future-posts.json')
    
    if not future_posts_file.exists():
        print("❌ future-posts.json not found")
        return None
    
    try:
        with open(future_posts_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("❌ Invalid JSON in future-posts.json")
        return None
    
    pending = data.get('pending', [])
    
    if not pending:
        print("❌ No pending posts in queue")
        return None
    
    # Get first pending post
    post = pending[0]
    title = post.get('title')
    category = post.get('category', 'النجوم')
    
    return title, category

def move_to_completed(title):
    """
    Move a post from pending to completed after successful generation
    """
    future_posts_file = Path('/root/arabfalak/data/future-posts.json')
    
    try:
        with open(future_posts_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        return False
    
    pending = data.get('pending', [])
    completed = data.get('completed', [])
    
    # Find and move the post
    for post in pending[:]:
        if post.get('title') == title:
            pending.remove(post)
            completed.insert(0, post)
            
            data['pending'] = pending
            data['completed'] = completed
            
            with open(future_posts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
    
    return False

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--mark-completed':
        if len(sys.argv) < 3:
            print("Usage: get_next_post.py --mark-completed '<title>'")
            sys.exit(1)
        title = sys.argv[2]
        if move_to_completed(title):
            print(f"✅ Moved '{title}' to completed")
            sys.exit(0)
        else:
            print(f"❌ Could not find '{title}' in pending posts")
            sys.exit(1)
    else:
        result = get_next_post()
        if result:
            title, category = result
            print(f"{title}|{category}")
            sys.exit(0)
        else:
            sys.exit(1)
