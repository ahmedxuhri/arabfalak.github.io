#!/bin/bash
set -e

cd /root/arabfalak || exit 1

# Get next post from the queue
NEXT_POST=$(/usr/bin/python3 /root/arabfalak/scripts/get_next_post.py)

if [ $? -ne 0 ]; then
    echo "❌ No posts in queue"
    exit 0
fi

# Parse title and category
TITLE=$(echo "$NEXT_POST" | cut -d'|' -f1)
CATEGORY=$(echo "$NEXT_POST" | cut -d'|' -f2)

echo "📝 Generating post: $TITLE"

# Generate the post
/usr/bin/python3 /root/arabfalak/scripts/generate_post.py --topic "$TITLE" --category "$CATEGORY" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Post generated successfully"
    
    # Mark as completed in the queue
    /usr/bin/python3 /root/arabfalak/scripts/get_next_post.py --mark-completed "$TITLE"
    
    # Auto-deploy to GitHub Pages (the deploy.sh script will handle it)
    echo "🚀 Deploying to GitHub Pages..."
    /root/arabfalak/scripts/deploy.sh
else
    echo "❌ Failed to generate post"
    exit 1
fi
