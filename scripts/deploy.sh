#!/bin/bash
set -e

cd /root/arabfalak || exit 1

# Check if there are any uncommitted changes
if git diff-index --quiet HEAD --; then
    echo "No changes to commit"
    exit 0
fi

# Stage all changes
git add -A

# Commit with timestamp
git commit -m "Auto-deploy: $(date '+%Y-%m-%d %H:%M:%S')" \
    --no-verify \
    -q || {
    echo "No changes to commit (git commit returned non-zero)"
    exit 0
}

# Push to GitHub
git push origin main -q

echo "✅ Changes deployed to GitHub Pages at $(date '+%Y-%m-%d %H:%M:%S')"
