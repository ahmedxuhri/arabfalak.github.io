#!/bin/bash

# Setup cron job for daily post generation
CRON_JOB="0 8 * * * /usr/bin/python3 /root/arabfalak/scripts/generate_post.py >> /var/log/arabfalak_cron.log 2>&1"

echo "⏳ جاري إضافة وظيفة Cron..."

(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ تم إضافة وظيفة Cron بنجاح"
echo "⏰ المقالات ستُنشر يومياً الساعة 08:00 UTC"
echo "📋 السجل: /var/log/arabfalak_cron.log"
