#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime


def format_date_arabic(date_str):
    """Format ISO date to Arabic format."""
    try:
        date_obj = datetime.fromisoformat(date_str)
        months = [
            'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
            'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
        ]
        day = date_obj.day
        month = months[date_obj.month - 1]
        year = date_obj.year
        return f"{day} {month} {year}"
    except:
        return date_str


def update_index():
    """Generate index.html from siteurls.json"""
    siteurls_file = Path('/root/arabfalak/data/siteurls.json')
    
    try:
        with open(siteurls_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)
    except:
        posts = []
    
    # Build post cards
    posts_html = ''
    for post in posts[:12]:  # Show 12 per page
        title = post.get('title', 'بدون عنوان')
        url = post.get('url', '/')
        category = post.get('category', 'عام')
        excerpt = post.get('excerpt', '')[:150]
        date_published = post.get('date_published', '')
        date_arabic = format_date_arabic(date_published)
        
        posts_html += f'''    <article class="post-card">
      <span class="post-category">{category}</span>
      <h3><a href="{url}" style="text-decoration: none; color: inherit;">{title}</a></h3>
      <time>{date_arabic}</time>
      <p class="excerpt">{excerpt}...</p>
      <a href="{url}" class="read-more">اقرأ المزيد →</a>
    </article>
'''
    
    # Build pagination if needed
    pagination_html = ''
    if len(posts) > 12:
        pagination_html = '''    <div class="pagination">
      <span class="current">1</span>
    </div>
'''
    
    # Build complete HTML
    header = '''<header class="site-header">
  <div class="container">
    <a href="/" class="site-logo">عرب فلك</a>
    <nav class="site-nav" aria-label="التنقل الرئيسي">
      <button class="nav-toggle" aria-label="فتح القائمة">&#9776;</button>
      <ul>
        <li><a href="/">الرئيسية</a></li>
        <li><a href="/categories/solar-system/">المجموعة الشمسية</a></li>
        <li><a href="/categories/deep-space/">الفضاء العميق</a></li>
        <li><a href="/categories/stars/">النجوم</a></li>
        <li><a href="/about/">عن الموقع</a></li>
      </ul>
    </nav>
  </div>
</header>'''

    footer = '''<footer class="site-footer">
  <div class="container">
    <p class="footer-tagline">عرب فلك — علم الفلك بالعربية</p>
    <p class="footer-links">
      <a href="/sitemap.xml">خريطة الموقع</a> ·
      <a href="https://twitter.com/arabfalak" rel="noopener" target="_blank">تويتر</a> ·
      <a href="https://t.me/arabfalak" rel="noopener" target="_blank">تيليغرام</a>
    </p>
    <p class="footer-copy">&copy; <span id="year"></span> عرب فلك. جميع الحقوق محفوظة.</p>
  </div>
  <script>document.getElementById('year').textContent = new Date().getFullYear();</script>
</footer>'''

    meta_description = "موقع عرب فلك — مقالات علمية متخصصة في علم الفلك باللغة العربية. استكشف النجوم والمجرات والثقوب السوداء وأسرار الكون."
    
    html = f'''<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>عرب فلك — علم الفلك بالعربية</title>
  <meta name="description" content="{meta_description}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://www.arabfalak.com/">
  
  <!-- Open Graph -->
  <meta property="og:title" content="عرب فلك — علم الفلك بالعربية">
  <meta property="og:description" content="{meta_description}">
  <meta property="og:image" content="https://www.arabfalak.com/assets/og-default.jpg">
  <meta property="og:url" content="https://www.arabfalak.com/">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="ar_AR">
  
  <!-- Preload font -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap">
  <link rel="stylesheet" href="/assets/css/style.css">
  
  <!-- JSON-LD -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "عرب فلك",
    "url": "https://www.arabfalak.com",
    "description": "{meta_description}",
    "potentialAction": {{
      "@type": "SearchAction",
      "target": "https://www.arabfalak.com?s={{search_term_string}}"
    }}
  }}
  </script>
</head>
<body dir="rtl" lang="ar">
  {header}
  
  <main>
    <div class="container">
      <h1>عرب فلك — علم الفلك بالعربية</h1>
      <p style="font-size: 1.2em; color: #bbb; margin-bottom: 2rem;">
        مرحباً بك في أكبر موقع عربي متخصص في علم الفلك. استكشف النجوم والمجرات والثقوب السوداء وأسرار الكون.
      </p>
      
      <section class="posts-grid">
        {posts_html}
      </section>
      
      {pagination_html}
    </div>
  </main>
  
  {footer}
  <script src="/assets/js/main.js" defer></script>
</body>
</html>'''
    
    # Write file
    index_file = Path('/root/arabfalak/index.html')
    index_file.write_text(html, encoding='utf-8')
    print(f"✅ تم تحديث: {index_file}")


if __name__ == '__main__':
    update_index()
