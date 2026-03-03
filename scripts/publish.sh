#!/bin/bash

# DNS records you must add at your registrar:
# A     @    185.199.108.153
# A     @    185.199.109.153
# A     @    185.199.110.153
# A     @    185.199.111.153
# CNAME www  arabfalak.github.io
# Then: GitHub repo Settings → Pages → Custom domain: arabfalak.com → Enforce HTTPS

cd /root/arabfalak || exit 1

git add -A
git commit -m "${1:-تحديث الموقع $(date '+%Y-%m-%d %H:%M:%S')}"
git push origin main

echo "✅ تم رفع التحديثات إلى GitHub"
