#!/usr/bin/env python3
import os
import sys
import json
import argparse
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
import subprocess

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_BASE_URL = 'https://api.deepseek.com/v1'

# Topics list (30 topics)
TOPICS_LIST = [
    "دورة حياة النجوم: من السديم إلى الثقب الأسود",
    "الثقوب السوداء: بوابات الفضاء الغامضة",
    "المجرات: جزر الكون البعيدة",
    "الكواكب الخارجية: البحث عن حياة خارج الأرض",
    "علم الكونيات: نشأة الكون وتطوره",
    "المجموعة الشمسية: نظامنا الكوكبي",
    "القمر: قمرنا وأسراره",
    "المريخ: الكوكب الأحمر والاستكشاف البشري",
    "المذنبات والنيازك: زوار من الفضاء",
    "الثقب الأسود الهائل: في قلب مجرتنا",
    "موجات الجاذبية: موسيقى الكون",
    "الطاقة المظلمة والمادة المظلمة",
    "التلسكوبات الفضائية: نوافذنا إلى الكون",
    "أضواء النجوم: كيف نحسب مسافات الكون",
    "المجال المغناطيسي الشمسي وتأثيره",
    "الرياح الشمسية: تأثيرها على الأرض",
    "الانفجارات النجمية والمستعرات الفائقة",
    "النجوم النيوترونية: أكثر الأجسام كثافة",
    "النظام الثنائي: رقصة النجوم",
    "الأقمار الطبيعية في النظام الشمسي",
    "المسابير الفضائية الحالية والمستقبلية",
    "محطة الفضاء الدولية: منزلنا في الفضاء",
    "تاريخ الفلك العربي القديم",
    "الفلكيون العرب المسلمون",
    "التقويم القمري والحسابات الفلكية",
    "الخسوف والكسوف: ظواهر فلكية مذهلة",
    "النقطة الدنيا والعليا: مدارات الأقمار الصناعية",
    "الطيف الكهرومغناطيسي وأنواع الإشعاع",
    "الحياة على الأرض: من أين جاءت؟",
    "مستقبل الاستكشاف الفضائي البشري",
]

try:
    import requests
except ImportError:
    print("خطأ: مكتبة requests غير مثبتة. يرجى تثبيتها: pip install requests python-dotenv")
    sys.exit(1)


def call_deepseek_api(system_prompt, user_prompt):
    """
    Call DeepSeek API to generate post content.
    """
    if not DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY not found in .env file")
    
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        'temperature': 0.7,
        'max_tokens': 8000
    }
    
    try:
        response = requests.post(
            f'{DEEPSEEK_BASE_URL}/chat/completions',
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"خطأ في الاتصال بـ DeepSeek API: {e}")
        sys.exit(1)


def extract_json_from_response(response_text):
    """
    Extract JSON from the API response, handling markdown code blocks.
    """
    # Try to find JSON in code blocks
    json_match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', response_text)
    if json_match:
        json_str = json_match.group(1).strip()
    else:
        # Try to parse the whole response as JSON
        json_str = response_text.strip()
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"خطأ في تحليل JSON من الرد: {e}")
        print(f"الرد: {response_text[:500]}")
        sys.exit(1)


def fetch_web_search_results(topic):
    """
    Fetch web search results for the topic using DeepSeek web search.
    For now, return a placeholder that the API should enhance.
    """
    # In a real implementation, this would call a web search API
    # For now, we return a generic prompt for DeepSeek to use
    return f"(استخدم معرفتك المحدثة عن موضوع: {topic})"


def generate_slug(title):
    """
    Convert Arabic title to English slug.
    """
    # Simple transliteration mapping
    slug = title.lower()
    # Remove Arabic diacritics and special characters
    slug = re.sub(r'[\u064B-\u0652]', '', slug)
    # Replace common Arabic characters with Latin
    mapping = {
        'أ': 'a', 'إ': 'i', 'آ': 'aa',
        'ب': 'b', 'ت': 't', 'ث': 'th',
        'ج': 'j', 'ح': 'h', 'خ': 'kh',
        'د': 'd', 'ذ': 'dh', 'ر': 'r',
        'ز': 'z', 'س': 's', 'ش': 'sh',
        'ص': 's', 'ض': 'd', 'ط': 't',
        'ظ': 'z', 'ع': 'a', 'غ': 'gh',
        'ف': 'f', 'ق': 'q', 'ك': 'k',
        'ل': 'l', 'م': 'm', 'ن': 'n',
        'ه': 'h', 'و': 'w', 'ي': 'y',
        'ة': 'a', 'ء': ''
    }
    for ar, en in mapping.items():
        slug = slug.replace(ar, en)
    # Remove non-alphanumeric
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Remove consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    # Limit length
    slug = slug[:50].strip('-')
    return slug or 'post'


def format_date_arabic(date_str):
    """
    Format ISO date to Arabic format.
    """
    try:
        date_obj = datetime.fromisoformat(date_str)
        # Arabic month names
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


def build_html_file(post_data, related_posts):
    """
    Build complete HTML file from post data.
    """
    today = datetime.now().strftime('%Y-%m-%d')
    date_arabic = format_date_arabic(today)
    
    slug = post_data.get('slug', generate_slug(post_data['title']))
    title = post_data['title']
    category = post_data.get('category', 'عام')
    excerpt = post_data.get('excerpt', '')
    meta_description = post_data.get('meta_description', '')
    
    # Build TOC
    toc_items = ''
    for toc_item in post_data.get('toc', []):
        section_id = toc_item.get('id', '')
        section_title = toc_item.get('title', '')
        if section_id and section_title:
            toc_items += f'<li><a href="#{section_id}">{section_title}</a></li>\n'
    
    # Build sections
    sections_html = ''
    for section in post_data.get('sections', []):
        section_id = section.get('id', '')
        h2 = section.get('h2', '')
        content = section.get('content', '')
        has_callout = section.get('has_callout', False)
        callout = section.get('callout', {})
        has_table = section.get('has_table', False)
        table = section.get('table', None)
        
        sections_html += f'<section id="{section_id}">\n'
        sections_html += f'<h2>{h2}</h2>\n'
        sections_html += f'<p>{content}</p>\n'
        
        if has_callout and callout:
            callout_type = callout.get('type', 'fact')
            callout_text = callout.get('text', '')
            sections_html += f'<div class="callout-{callout_type}">{callout_text}</div>\n'
        
        if has_table and table:
            sections_html += build_table_html(table)
        
        sections_html += '</section>\n'
    
    # Build Mermaid chart
    mermaid_html = ''
    if post_data.get('has_mermaid_chart'):
        mermaid_chart = post_data.get('mermaid_chart', '')
        if mermaid_chart:
            mermaid_html = f'<section class="mermaid-section">\n<h2>رسم توضيحي</h2>\n<div class="mermaid">\n{mermaid_chart}\n</div>\n</section>\n'
    
    # Build FAQ
    faq_html = ''
    faq_items = post_data.get('faq', [])
    if faq_items:
        faq_schema = []
        for faq_item in faq_items:
            question = faq_item.get('question', '')
            answer = faq_item.get('answer', '')
            faq_html += f'<details>\n<summary>{question}</summary>\n<p>{answer}</p>\n</details>\n'
            faq_schema.append({
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": answer
                }
            })
    
    # Build related posts
    related_html = ''
    if related_posts:
        for post in related_posts:
            related_html += f'<li><a href="{post["url"]}">{post["anchor_text"]}</a></li>\n'
    
    # Build external links
    external_html = ''
    for link in post_data.get('external_links', []):
        link_text = link.get('text', '')
        link_url = link.get('url', '#')
        rel = link.get('rel', 'nofollow')
        external_html += f'<li><a href="{link_url}" rel="{rel}" target="_blank">{link_text}</a></li>\n'
    
    # Header and Footer
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

    # Build complete HTML
    category_slug = slug.split('-')[0]
    schema_keywords = post_data.get('schema_article_keywords', '')
    
    html = f'''<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | عرب فلك</title>
  <meta name="description" content="{meta_description}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://www.arabfalak.com/posts/{slug}/">
  
  <!-- Open Graph -->
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{post_data.get('og_description', meta_description)}">
  <meta property="og:image" content="https://www.arabfalak.com/assets/og-default.jpg">
  <meta property="og:url" content="https://www.arabfalak.com/posts/{slug}/">
  <meta property="og:type" content="article">
  <meta property="og:locale" content="ar_AR">
  <meta property="og:site_name" content="عرب فلك">
  
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{meta_description}">
  <meta name="twitter:image" content="https://www.arabfalak.com/assets/og-default.jpg">
  
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
    "@graph": [
      {{
        "@type": "Article",
        "headline": "{title}",
        "description": "{meta_description}",
        "keywords": "{schema_keywords}",
        "inLanguage": "ar",
        "url": "https://www.arabfalak.com/posts/{slug}/",
        "datePublished": "{today}",
        "dateModified": "{today}",
        "author": {{"@type": "Organization", "name": "عرب فلك"}},
        "publisher": {{
          "@type": "Organization",
          "name": "عرب فلك",
          "url": "https://www.arabfalak.com"
        }}
      }},
      {{
        "@type": "FAQPage",
        "mainEntity": {json.dumps(faq_schema, ensure_ascii=False)}
      }},
      {{
        "@type": "BreadcrumbList",
        "itemListElement": [
          {{"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": "https://www.arabfalak.com/"}},
          {{"@type": "ListItem", "position": 2, "name": "{category}", "item": "https://www.arabfalak.com/categories/{category_slug}/"}},
          {{"@type": "ListItem", "position": 3, "name": "{title}", "item": "https://www.arabfalak.com/posts/{slug}/"}}
        ]
      }}
    ]
  }}
  </script>
</head>
<body dir="rtl" lang="ar">
  {header}
  
  <main>
    <article class="post-article" itemscope itemtype="https://schema.org/Article">
      <nav class="breadcrumb" aria-label="مسار التنقل">
        <a href="/">الرئيسية</a> /
        <a href="/categories/{category_slug}/">{category}</a> /
        <span>{title}</span>
      </nav>
      
      <header class="post-header">
        <div class="post-meta">
          <span class="post-category">{category}</span>
          <time datetime="{today}">{date_arabic}</time>
        </div>
        <h1 itemprop="headline">{title}</h1>
        <p class="post-excerpt">{excerpt}</p>
      </header>
      
      <div class="hero-placeholder" role="img" aria-label="صورة توضيحية لـ {title}">
        <span class="hero-placeholder-text">صورة: {title}</span>
      </div>
      
      <nav class="toc" aria-label="محتويات المقال">
        <h2 class="toc-title">محتويات المقال</h2>
        <ol>
          {toc_items}
        </ol>
      </nav>
      
      <div class="post-content" itemprop="articleBody">
        <section id="introduction">
          <h2>المقدمة</h2>
          <p>{post_data.get('introduction', '')}</p>
        </section>
        
        {sections_html}
        
        {mermaid_html}
        
        <section class="related-posts" aria-label="مقالات ذات صلة">
          <h2>مقالات ذات صلة</h2>
          <ul>
            {related_html if related_html else '<li>لا توجد مقالات ذات صلة حتى الآن</li>'}
          </ul>
        </section>
        
        <section class="faq-section" aria-labelledby="faq-heading">
          <h2 id="faq-heading">أسئلة شائعة</h2>
          {faq_html}
        </section>
        
        <section id="conclusion">
          <h2>خلاصة القول</h2>
          <p>{post_data.get('conclusion', '')}</p>
        </section>
        
        <section class="external-sources">
          <h2>مصادر ومراجع</h2>
          <ul>
            {external_html}
          </ul>
        </section>
      </div>
    </article>
  </main>
  
  {footer}
  
  {'<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script><script>mermaid.contentLoaded();</script>' if mermaid_html else ''}
  <script src="/assets/js/main.js" defer></script>
</body>
</html>'''
    
    return html, slug


def build_table_html(table):
    """
    Build HTML table from table data.
    """
    if not table or 'headers' not in table or 'rows' not in table:
        return ''
    
    html = '<table>\n<thead>\n<tr>\n'
    for header in table.get('headers', []):
        html += f'<th>{header}</th>\n'
    html += '</tr>\n</thead>\n<tbody>\n'
    
    for row in table.get('rows', []):
        html += '<tr>\n'
        for cell in row:
            html += f'<td>{cell}</td>\n'
        html += '</tr>\n'
    
    html += '</tbody>\n</table>\n'
    return html


def main():
    parser = argparse.ArgumentParser(description='Generate astronomy blog post')
    parser.add_argument('--topic', type=str, help='Topic for the post')
    args = parser.parse_args()
    
    topic = args.topic or TOPICS_LIST[0]
    
    print(f"📝 جاري توليد مقال عن: {topic}")
    
    # System prompt
    system_prompt = """أنت كاتب محتوى متخصص في علم الفلك باللغة العربية الفصحى. تكتب مقالات علمية دقيقة وجذابة للقراء العرب المهتمين بالفضاء والفلك. أسلوبك واضح ومبسط دون إخلال بالدقة العلمية. تستخدم المصطلحات العلمية العربية الصحيحة وتشرحها عند الحاجة."""
    
    # User prompt
    user_prompt = f"""اكتب مقالاً فلكياً شاملاً باللغة العربية الفصحى عن الموضوع: "{topic}"

يجب أن يحتوي المقال على العناصر التالية بالترتيب، وتخرج النتيجة كـ JSON فقط بدون أي نص خارجه:

{{
  "title": "عنوان المقال (50-60 حرف، يحتوي الكلمة المفتاحية)",
  "slug": "url-slug-in-english-lowercase-hyphens",
  "focus_keyphrase": "الكلمة المفتاحية المحورية",
  "meta_description": "وصف ميتا 150-160 حرف يحتوي الكلمة المفتاحية ويشجع على النقر",
  "og_description": "نفس الوصف أو نسخة محسّنة للشبكات الاجتماعية",
  "excerpt": "مقتطف 80-100 كلمة يلخص المقال",
  "category": "التصنيف (اختر من: النجوم / المجموعة الشمسية / المجرات / الثقوب السوداء / الكواكب الخارجية / علم الكونيات / المهمات الفضائية / التلسكوبات / علماء الفلك العرب / فيزياء الفضاء)",
  "tags": ["وسم1", "وسم2", "وسم3", "وسم4", "وسم5"],
  "tfidf_tokens": ["كلمة1", "كلمة2", "كلمة3", "كلمة4", "كلمة5", "كلمة6", "كلمة7", "كلمة8", "كلمة9", "كلمة10"],
  "toc": [
    {{"id": "section-1", "title": "العنوان الأول"}},
    {{"id": "section-2", "title": "العنوان الثاني"}},
    {{"id": "section-3", "title": "العنوان الثالث"}}
  ],
  "introduction": "مقدمة 150-250 كلمة: ابدأ بحقيقة مذهلة أو سؤال، ثم قدّم الموضوع",
  "sections": [
    {{
      "id": "section-1",
      "h2": "عنوان القسم الأول",
      "content": "محتوى القسم 300-400 كلمة، فقرات واضحة ومختصرة",
      "has_table": false,
      "table": null,
      "has_callout": true,
      "callout": {{"type": "fact", "text": "حقيقة مهمة عن الموضوع"}}
    }},
    {{
      "id": "section-2",
      "h2": "عنوان القسم الثاني",
      "content": "محتوى آخر",
      "has_table": true,
      "table": {{
        "headers": ["العمود الأول", "العمود الثاني", "العمود الثالث"],
        "rows": [["قيمة1", "قيمة2", "قيمة3"], ["قيمة4", "قيمة5", "قيمة6"]]
      }},
      "has_callout": false,
      "callout": null
    }},
    {{
      "id": "section-3",
      "h2": "عنوان القسم الثالث",
      "content": "محتوى مفيد",
      "has_table": false,
      "table": null,
      "has_callout": true,
      "callout": {{"type": "tip", "text": "نصيحة مفيدة للقارئ"}}
    }}
  ],
  "has_mermaid_chart": true,
  "mermaid_chart": "graph TD\\n  A[النقطة الأولى] --> B[النقطة الثانية]\\n  B --> C[النقطة الثالثة]",
  "faq": [
    {{"question": "ما هو السؤال الأول؟", "answer": "إجابة واضحة ومختصرة"}},
    {{"question": "ما هو السؤال الثاني؟", "answer": "إجابة أخرى"}}
  ],
  "external_links": [
    {{"text": "مصدر خارجي موثوق", "url": "https://example.com", "rel": "dofollow"}},
    {{"text": "مصدر آخر", "url": "https://example.org", "rel": "dofollow"}}
  ],
  "conclusion": "خاتمة 100-150 كلمة: لخّص النقاط الرئيسية",
  "schema_article_keywords": "كلمة1، كلمة2، كلمة3، كلمة4، كلمة5"
}}

متطلبات إضافية:
- الكلمات الإجمالية: 2500-3500 كلمة
- جمل واضحة لا تتجاوز 20 كلمة بالمتوسط
- 5-7 روابط خارجية لمصادر موثوقة (NASA, ESA, Wikipedia العربية)
- 3-5 أسئلة شائعة في FAQ
- يجب أن تكون الروابط الخارجية حقيقية وموثوقة"""
    
    # Call API
    print("⏳ جاري استدعاء API...")
    response = call_deepseek_api(system_prompt, user_prompt)
    
    # Parse response
    print("📖 جاري تحليل الرد...")
    post_data = extract_json_from_response(response)
    
    # Get related posts
    from tfidf_linker import get_related_posts
    related_posts = get_related_posts(post_data.get('tfidf_tokens', []))
    
    # Build HTML
    html_content, slug = build_html_file(post_data, related_posts)
    
    # Write HTML file
    post_dir = Path('/root/arabfalak/posts') / slug
    post_dir.mkdir(parents=True, exist_ok=True)
    html_file = post_dir / 'index.html'
    html_file.write_text(html_content, encoding='utf-8')
    print(f"✅ تم إنشاء الملف: {html_file}")
    
    # Update siteurls.json
    today = datetime.now().strftime('%Y-%m-%d')
    siteurls_file = Path('/root/arabfalak/data/siteurls.json')
    
    try:
        with open(siteurls_file, 'r', encoding='utf-8') as f:
            siteurls = json.load(f)
    except:
        siteurls = []
    
    new_entry = {
        'title': post_data.get('title'),
        'slug': slug,
        'url': f'/posts/{slug}/',
        'category': post_data.get('category'),
        'tags': post_data.get('tags', []),
        'focus_keyphrase': post_data.get('focus_keyphrase'),
        'excerpt': post_data.get('excerpt'),
        'date_published': today,
        'tfidf_tokens': post_data.get('tfidf_tokens', [])
    }
    
    siteurls.insert(0, new_entry)
    with open(siteurls_file, 'w', encoding='utf-8') as f:
        json.dump(siteurls, f, ensure_ascii=False, indent=2)
    print(f"✅ تم تحديث: {siteurls_file}")
    
    # Update index.html
    print("🔄 جاري تحديث الصفحة الرئيسية...")
    subprocess.run(['/usr/bin/python3', '/root/arabfalak/scripts/update_index.py'], check=False)
    
    # Update sitemap.xml
    print("🔄 جاري تحديث خريطة الموقع...")
    subprocess.run(['/usr/bin/python3', '/root/arabfalak/scripts/update_sitemap.py'], check=False)
    
    print(f"\n✨ تم إنشاء المقال بنجاح!")
    print(f"📄 الملف: {html_file}")
    print(f"🔗 الرابط: https://www.arabfalak.com/posts/{slug}/")


if __name__ == '__main__':
    main()
