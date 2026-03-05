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

# Load environment variables from the arabfalak directory
from dotenv import load_dotenv
env_file = Path(__file__).parent.parent / '.env'
load_dotenv(env_file, override=True)

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
        'max_tokens': 8192
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
  <link rel="canonical" href="https://www.arabfalak.com/{slug}/">
  
  <!-- Open Graph -->
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{post_data.get('og_description', meta_description)}">
  <meta property="og:image" content="https://www.arabfalak.com/assets/og-default.jpg">
  <meta property="og:url" content="https://www.arabfalak.com/{slug}/">
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
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap" media="print" onload="this.media='all'">
  <noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap"></noscript>
  <link rel="stylesheet" href="/assets/css/style.min.css">
  
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
        "url": "https://www.arabfalak.com/{slug}/",
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
        "mainEntity": {json.dumps(faq_schema, ensure_ascii=False)[:1500]}
      }},
      {{
        "@type": "BreadcrumbList",
        "itemListElement": [
          {{"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": "https://www.arabfalak.com/"}},
          {{"@type": "ListItem", "position": 2, "name": "{category}", "item": "https://www.arabfalak.com/categories/{category_slug}/"}},
          {{"@type": "ListItem", "position": 3, "name": "{title}", "item": "https://www.arabfalak.com/{slug}/"}}
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
  
  {'<script async src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js" onload="mermaid.contentLoaded();"></script>' if mermaid_html else ''}
  <script src="/assets/js/main.min.js" defer></script>
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
    parser.add_argument('--category', type=str, help='Category for the post')
    args = parser.parse_args()
    
    topic = args.topic or TOPICS_LIST[0]
    
    print(f"📝 جاري توليد مقال عن: {topic}")
    
    # System prompt
    system_prompt = """أنت كاتب محتوى متخصص في علم الفلك باللغة العربية الفصحى. تكتب مقالات علمية دقيقة وجذابة للقراء العرب المهتمين بالفضاء والفلك. أسلوبك واضح ومبسط دون إخلال بالدقة العلمية. تستخدم المصطلحات العلمية العربية الصحيحة وتشرحها عند الحاجة."""
    
    # User prompt
    user_prompt = f"""اكتب مقالاً فلكياً شاملاً ومتعمقاً باللغة العربية الفصحى عن الموضوع: "{topic}"

المقال يجب أن يكون:
- متخصص وعميق: استهدف قراء لديهم معرفة أساسية وتريد توسيع معرفتهم
- شامل: اشرح المفاهيم من جميع الجوانب (تاريخي، علمي، عملي، مستقبلي)
- مثير: ابدأ بحقيقة مذهلة أو لغز كوني
- مرجع: اجعله مرجعاً يعود إليه القارئ مجدداً

يجب أن يحتوي المقال على العناصر التالية بالترتيب، وتخرج النتيجة كـ JSON فقط بدون أي نص خارجه:

{{
  "title": "عنوان جذاب (60-70 حرف، يحتوي الكلمة المفتاحية، يثير الفضول)",
  "slug": "url-slug-in-english-lowercase-hyphens",
  "focus_keyphrase": "الكلمة المفتاحية المحورية الرئيسية",
  "meta_description": "وصف ميتا 155-165 حرف يحتوي الكلمة المفتاحية ويشجع على النقر - يجب أن يكون جذاباً ومباشراً",
  "og_description": "وصف محسّن للشبكات الاجتماعية (160-170 حرف) - يجب أن يكون مختلفاً وجذاباً بصرياً",
  "excerpt": "مقتطف 100-150 كلمة يلخص المقال بشكل شامل - يعطي القارئ فكرة كاملة عن المحتوى",
  "author_note": "ملاحظة من الكاتب (50-80 كلمة) توضح أهمية الموضوع أو خبرة شخصية",
  "category": "التصنيف (اختر من: النجوم / المجموعة الشمسية / المجرات / الثقوب السوداء / الكواكب الخارجية / علم الكونيات / المهمات الفضائية / التلسكوبات / علماء الفلك العرب / فيزياء الفضاء)",
  "tags": ["وسم1", "وسم2", "وسم3", "وسم4", "وسم5", "وسم6", "وسم7"],
  "tfidf_tokens": ["كلمة1", "كلمة2", "كلمة3", "كلمة4", "كلمة5", "كلمة6", "كلمة7", "كلمة8", "كلمة9", "كلمة10", "كلمة11", "كلمة12", "كلمة13", "كلمة14", "كلمة15"],
  "reading_time": "وقت القراءة بالدقائق (رقم صحيح، مثل: 8)",
  "difficulty_level": "مستوى الصعوبة (سهل / متوسط / متقدم)",
  "toc": [
    {{"id": "what-is", "title": "ما هو/هي {الموضوع}؟"}},
    {{"id": "history", "title": "التاريخ والاكتشافات"}},
    {{"id": "characteristics", "title": "الخصائص والمميزات الرئيسية"}},
    {{"id": "impact", "title": "التأثير والأهمية العلمية"}},
    {{"id": "research", "title": "الأبحاث الحالية والمستقبلية"}},
    {{"id": "interesting-facts", "title": "حقائق وملاحظات مثيرة للاهتمام"}},
    {{"id": "related-phenomena", "title": "الظواهر والمفاهيم المرتبطة"}}
  ],
  "introduction": "مقدمة متعمقة 250-300 كلمة: ابدأ بحقيقة مذهلة أو سؤال فلسفي، ثم قدّم الموضوع بشكل شامل، وضح لماذا يهم القارئ",
  "sections": [
    {{
      "id": "what-is",
      "h2": "ما هو/هي {الموضوع}؟",
      "h3_subsections": [
        {{"title": "التعريف العلمي", "content": "200-250 كلمة - اشرح بوضوح وبساطة مع الدقة"}},
        {{"title": "المقياس والحجم", "content": "150-200 كلمة - استخدم المقارنات لتوضيح الحجم"}},
        {{"title": "المكونات الأساسية", "content": "200-250 كلمة - شرح العناصر المكونة"}}
      ],
      "has_table": true,
      "table": {{
        "title": "جدول مقارنة/معلومات",
        "headers": ["الخاصية", "القيمة/الوصف", "ملاحظات"],
        "rows": [["مثال1", "وصف", "ملاحظة"], ["مثال2", "وصف", "ملاحظة"], ["مثال3", "وصف", "ملاحظة"]]
      }},
      "has_callout": true,
      "callout": {{"type": "definition", "title": "تعريف مهم", "text": "تعريف واضح للمفهوم الأساسي"}}
    }},
    {{
      "id": "history",
      "h2": "التاريخ والاكتشافات",
      "h3_subsections": [
        {{"title": "الاكتشاف الأول", "content": "200-250 كلمة - متى وكيف وبواسطة من"}},
        {{"title": "التطور عبر الزمن", "content": "250-300 كلمة - كيف تطورت معرفتنا"}},
        {{"title": "الاكتشافات الحديثة", "content": "200-250 كلمة - أحدث التطورات"}}
      ],
      "has_table": true,
      "table": {{
        "title": "جدول زمني للاكتشافات",
        "headers": ["السنة", "الحدث", "العالم/المهمة"],
        "rows": [["سنة", "الاكتشاف", "المكتشف"], ["سنة", "الاكتشاف", "المكتشف"]]
      }},
      "has_callout": true,
      "callout": {{"type": "history", "title": "حقيقة تاريخية", "text": "حقيقة تاريخية مثيرة عن الاكتشاف"}}
    }},
    {{
      "id": "characteristics",
      "h2": "الخصائص والمميزات الرئيسية",
      "h3_subsections": [
        {{"title": "الخصائص الفيزيائية", "content": "250-300 كلمة - درجات الحرارة، الضغط، التركيب، إلخ"}},
        {{"title": "الخصائص الكيميائية والبيولوجية", "content": "200-250 كلمة - إن وجدت"}},
        {{"title": "الخصائص الديناميكية", "content": "200-250 كلمة - الحركة والتفاعلات"}}
      ],
      "has_table": true,
      "table": {{
        "title": "الخصائص المقاسة والمعروفة",
        "headers": ["الخاصية", "القيمة", "وحدة القياس"],
        "rows": [["خاصية1", "قيمة", "وحدة"], ["خاصية2", "قيمة", "وحدة"]]
      }},
      "has_callout": true,
      "callout": {{"type": "fact", "title": "حقيقة علمية", "text": "حقيقة مذهلة عن الخصائص"}}
    }},
    {{
      "id": "impact",
      "h2": "التأثير والأهمية العلمية",
      "h3_subsections": [
        {{"title": "الأهمية العلمية", "content": "250-300 كلمة - لماذا يدرسها العلماء"}},
        {{"title": "التأثير على فهمنا للكون", "content": "200-250 كلمة - كيف غيرت نظرتنا"}},
        {{"title": "التطبيقات العملية", "content": "200-250 كلمة - الفوائد العملية إن وجدت"}}
      ],
      "has_callout": true,
      "callout": {{"type": "importance", "title": "لماذا يهم؟", "text": "شرح موجز لأهميتها في حياتنا"}}
    }},
    {{
      "id": "research",
      "h2": "الأبحاث الحالية والمستقبلية",
      "h3_subsections": [
        {{"title": "الأبحاث الجارية", "content": "250-300 كلمة - ما يبحث عنه العلماء حالياً"}},
        {{"title": "التلسكوبات والأدوات", "content": "200-250 كلمة - الأدوات المستخدمة في الدراسة"}},
        {{"title": "الخطط المستقبلية", "content": "200-250 كلمة - ما المخطط له في المستقبل"}}
      ],
      "has_table": true,
      "table": {{
        "title": "المهمات الفضائية والمشاريع البحثية",
        "headers": ["المهمة/المشروع", "الجهة المسؤولة", "الحالة"],
        "rows": [["مهمة1", "وكالة", "قيد التنفيذ"], ["مهمة2", "وكالة", "قيد الدراسة"]]
      }},
      "has_callout": true,
      "callout": {{"type": "future", "title": "آفاق المستقبل", "text": "نظرة مستقبلية على تطور الدراسات"}}
    }},
    {{
      "id": "interesting-facts",
      "h2": "حقائق ومعلومات مثيرة للاهتمام",
      "content": "400-500 كلمة - اجمع الحقائق الغريبة والمذهلة والقليل المعروف عن الموضوع",
      "has_callout": true,
      "callout": {{"type": "amazing-fact", "title": "حقيقة مدهشة", "text": "أكثر حقيقة غريبة وغير متوقعة"}}
    }},
    {{
      "id": "related-phenomena",
      "h2": "الظواهر والمفاهيم المرتبطة",
      "h3_subsections": [
        {{"title": "المفاهيم المرتبطة", "content": "250-300 كلمة - ما الذي يرتبط به هذا الموضوع"}},
        {{"title": "الاختلافات والفروقات", "content": "250-300 كلمة - ما الفرق بينه وبين أشياء مشابهة"}}
      ],
      "has_callout": true,
      "callout": {{"type": "connection", "title": "الربط مع مواضيع أخرى", "text": "كيف يرتبط هذا بمواضيع فلكية أخرى"}}
    }}
  ],
  "has_mermaid_chart": true,
  "mermaid_chart": "graph TD\\n  A[المفهوم الأساسي] --> B[التفاصيل]\\n  B --> C[التطبيقات]\\n  A --> D[الاكتشافات]\\n  D --> E[المستقبل]",
  "infographics_description": "وصف إنفوجرافيك محتمل: مثلاً 'خريطة لتطور فهمنا للموضوع عبر الزمن'",
  "faq": [
    {{"question": "ما هو {الموضوع} بكلمات بسيطة؟", "answer": "شرح بسيط وواضح يناسب المبتدئين (100-150 كلمة)"}},
    {{"question": "كيف يتم دراسة {الموضوع}؟", "answer": "شرح الطرق والأدوات المستخدمة (100-150 كلمة)"}},
    {{"question": "ما أهمية دراسة {الموضوع}؟", "answer": "شرح الفوائد والتأثير (100-150 كلمة)"}},
    {{"question": "ما أحدث الاكتشافات عن {الموضوع}؟", "answer": "معلومات عن أحدث الأبحاث (100-150 كلمة)"}},
    {{"question": "هل سيؤثر {الموضوع} على مستقبل البشرية؟", "answer": "نقاش فلسفي وعلمي (100-150 كلمة)"}},
    {{"question": "أين يمكن أن أتعلم المزيد؟", "answer": "اقتراحات للمصادر والموارد (80-100 كلمة)"}}
  ],
  "external_links": [
    {{"text": "مصدر موثوق من NASA", "url": "https://science.nasa.gov", "rel": "dofollow"}},
    {{"text": "مقالة من وكالة الفضاء الأوروبية", "url": "https://www.esa.int", "rel": "dofollow"}},
    {{"text": "دراسة علمية من مجلة متخصصة", "url": "https://example.com/research", "rel": "dofollow"}},
    {{"text": "مقالة من ويكيبيديا العربية", "url": "https://ar.wikipedia.org", "rel": "dofollow"}},
    {{"text": "مشروع بحثي من جامعة متخصصة", "url": "https://example.edu/research", "rel": "dofollow"}},
    {{"text": "مصدر تاريخي عن الاكتشاف", "url": "https://example.com/history", "rel": "dofollow"}},
    {{"text": "موقع متخصص بالفلك والفضاء", "url": "https://example.com/astronomy", "rel": "dofollow"}},
    {{"text": "مقالة من مجلة ساينس أو نيتشر", "url": "https://example.com/journal", "rel": "dofollow"}}
  ],
  "conclusion": "خاتمة شاملة 200-250 كلمة: لخّص النقاط الرئيسية، أعد التأكيد على الأهمية، اطرح سؤالاً مثيراً للتفكير، اشر إلى المستقبل",
  "schema_article_keywords": "كلمة1، كلمة2، كلمة3، كلمة4، كلمة5، كلمة6، كلمة7، كلمة8، كلمة9، كلمة10",
  "author_bio": "نبذة عن كاتب المقال (50-80 كلمة) - اذكر الخبرة والتخصص",
  "revision_notes": "ملاحظات عن تاريخ آخر تحديث أو تنقيح (50 كلمة)"
}}

متطلبات إضافية وإلزامية:
- الكلمات الإجمالية: 4500-5500 كلمة (مقال متعمق شامل)
- جمل واضحة لا تتجاوز 20 كلمة بالمتوسط
- 8-10 روابط خارجية لمصادر موثوقة (NASA, ESA, جامعات معروفة، مجلات علمية)
- 6-7 أسئلة شائعة في FAQ مع إجابات تفصيلية
- جداول معلومات واضحة (يجب أن تكون 2-3 جداول على الأقل)
- صناديق تنبيهات/حقائق (callouts) موزعة عبر المقال
- مخطط mermaid يوضح المفاهيم
- يجب أن تكون جميع الروابط الخارجية حقيقية وموثوقة وفعلية
- استخدم تنسيق صحيح للأرقام والوحدات العلمية
- أضف تعريفات واضحة للمصطلحات الفنية
- تأكد من التوازن بين العمق العلمي والوضوح للقارئ العام
- جودة الكتابة يجب أن تكون احترافية ومقنعة
- اجعل المقال ممتعاً وليس مملاً حتى مع العمق العلمي"""
    
    # Call API
    print("⏳ جاري استدعاء API...")
    response = call_deepseek_api(system_prompt, user_prompt)
    
    # Parse response
    print("📖 جاري تحليل الرد...")
    post_data = extract_json_from_response(response)
    
    # Override category if provided via CLI
    if args.category:
        post_data['category'] = args.category
    
    # Get related posts
    from tfidf_linker import get_related_posts
    related_posts = get_related_posts(post_data.get('tfidf_tokens', []))
    
    # Build HTML
    html_content, slug = build_html_file(post_data, related_posts)
    
    # Check for slug conflict
    conflict_check = subprocess.run(
        ['/usr/bin/python3', '/root/arabfalak/scripts/check_slug_conflict.py', slug],
        capture_output=True,
        text=True
    )
    
    if conflict_check.returncode != 0:
        print(f"❌ {conflict_check.stdout.strip()}")
        return
    
    print(conflict_check.stdout.strip())
    
    # Write HTML file at root level (not in /posts/ subdirectory)
    post_dir = Path('/root/arabfalak') / slug
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
        'url': f'/{slug}/',
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
    print(f"🔗 الرابط: https://www.arabfalak.com/{slug}/")


if __name__ == '__main__':
    main()
