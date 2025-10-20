import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from urllib.parse import urlparse

# --- 配置 ---
URL = "https://t.me/s/zaihuapd"
OUTPUT_DIR = "src/content/posts"
IMAGE_OUTPUT_DIR = "src/assets/images"
# --- 结束配置 ---

def download_image(url, post_id):
    """下载图片并保存到本地"""
    if not url:
        return None

    try:
        path = urlparse(url).path
        ext = os.path.splitext(path)[1]
        if not ext:
            ext = '.jpg'
            
        filename = f"{post_id}{ext}"
        filepath = os.path.join(IMAGE_OUTPUT_DIR, filename)

        img_response = requests.get(url, stream=True, timeout=20)
        img_response.raise_for_status()

        with open(filepath, 'wb') as f:
            for chunk in img_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"🖼️  成功下载图片: {filepath}")
        return filepath
    except requests.RequestException as e:
        print(f"❌ 下载图片失败 {url}: {e}")
        return None
    except Exception as e:
        print(f"❌ 保存图片时出错: {e}")
        return None

def create_markdown_file(post_id, title, published_date, local_image_path, body_content, source_text):
    """根据提取的信息生成 Markdown 文件内容"""
    
    # 【修改点】为 YAML frontmatter 准备标题
    # 1. 清理首尾空格
    clean_title = title.strip()
    # 2. 为 description 准备一个安全的版本（单引号包裹，并转义内部单引号）
    safe_description = clean_title.replace("'", "\\'")
    # 3. 为 title 准备双引号包裹的版本，并转义内部双引号
    escaped_title_for_yaml = clean_title.replace('"', '\\"')

    # 【修改点】生成 image 参数，不带引号
    image_frontmatter = "image: ''" # 默认值，带引号以表示空字符串
    if local_image_path:
        image_filename = os.path.basename(local_image_path)
        relative_image_path = f"../assets/images/{image_filename}"
        # 按要求移除路径的引号
        image_frontmatter = f"image: {relative_image_path}"

    body_markdown = f"## {clean_title}\n\n{body_content.strip()}\n\n"
    if source_text:
        body_markdown += f"*{source_text.strip()}*"

    # 【修改点】使用 f'''...''' 多行字符串来构建 frontmatter，并应用新的格式
    content = f'''---
title: "{escaped_title_for_yaml}"
published: {published_date}
description: '{safe_description}'
{image_frontmatter}
tags: [科技频道]
category: '科技频道'
draft: false
lang: ''
---

{body_markdown}
'''
    
    filename = f"kjpd{post_id}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 成功创建文件: {filepath}")
    except Exception as e:
        print(f"❌ 创建文件时出错 {filepath}: {e}")

def scrape_news():
    """主爬虫函数"""
    print("🚀 开始爬取新闻...")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(URL, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ 访问 {URL} 失败: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    messages = soup.find_all('div', class_='tgme_widget_message_wrap')
    
    if not messages:
        print("🟡 未找到任何新闻消息。")
        return

    print(f"🔍 找到 {len(messages)} 条消息，开始处理...")
    new_posts_count = 0
    for message_div in reversed(messages):
        widget_message = message_div.find('div', class_='js-widget_message')
        if not widget_message or 'data-post' not in widget_message.attrs:
            continue

        post_id = widget_message['data-post'].split('/')[-1]
        filename = f"kjpd{post_id}.md"
        filepath = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(filepath):
            continue
        
        new_posts_count += 1
        print(f"🆕 发现新文章，ID: {post_id}")

        message_text_div = widget_message.find('div', class_='js-message_text')
        if not message_text_div:
            continue

        title_tag = message_text_div.find('b')
        title = title_tag.get_text(strip=True) if title_tag else f"无标题新闻 - {post_id}"

        image_url = ''
        photo_wrap = widget_message.find('a', class_='tgme_widget_message_photo_wrap')
        if photo_wrap and 'style' in photo_wrap.attrs:
            match = re.search(r"url\('(.+?)'\)", photo_wrap['style'])
            if match:
                image_url = match.group(1)
        
        local_image_path = download_image(image_url, post_id)

        content_soup = BeautifulSoup(str(message_text_div), 'html.parser')
        if content_soup.b:
            content_soup.b.decompose()
        source_text = ''
        for link in reversed(content_soup.find_all('a')):
            if 't.me/' not in link.get('href', ''):
                source_text = link.get_text(strip=True)
                break
        for tag in content_soup.find_all(['a', 'i']):
            tag.decompose()
        body_content = content_soup.get_text(separator='\n', strip=True)
        body_content = re.sub(r'群友投稿补充\s*', '', body_content)
        
        published_date = datetime.now().strftime('%Y-%m-%d')
        create_markdown_file(post_id, title, published_date, local_image_path, body_content, source_text)

    if new_posts_count == 0:
        print("✅ 所有新闻都已是最新，无需更新。")
    else:
        print(f"🎉 处理完成，新增 {new_posts_count} 篇文章。")

if __name__ == "__main__":
    scrape_news()