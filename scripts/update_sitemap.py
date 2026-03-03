#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime


def update_sitemap():
    """Generate sitemap.xml from siteurls.json"""
    siteurls_file = Path('/root/arabfalak/data/siteurls.json')
    
    try:
        with open(siteurls_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)
    except:
        posts = []
    
    # Build sitemap entries
    sitemap_entries = '''  <url>
    <loc>https://www.arabfalak.com/</loc>
    <lastmod>''' + datetime.now().strftime('%Y-%m-%d') + '''</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
'''
    
    for post in posts:
        url = post.get('url', '/')
        date_published = post.get('date_published', datetime.now().strftime('%Y-%m-%d'))
        
        sitemap_entries += f'''  <url>
    <loc>https://www.arabfalak.com{url}</loc>
    <lastmod>{date_published}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
'''
    
    # Build complete sitemap
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_entries}
</urlset>'''
    
    # Write file
    sitemap_file = Path('/root/arabfalak/sitemap.xml')
    sitemap_file.write_text(sitemap, encoding='utf-8')
    print(f"✅ تم تحديث: {sitemap_file}")


if __name__ == '__main__':
    update_sitemap()
