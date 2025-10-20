import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from urllib.parse import urlparse # 新增导入，用于解析URL获取文件扩展名

# --- 配置 ---
URL = "https://t.me/s/zaihuapd"
OUTPUT_DIR = "src/content/posts"
IMAGE_OUTPUT_DIR = "src/assets/images" # 新增：图片保存目录
# --- 结束配置 ---

def download_image(url, post_id):
    """下载图片并保存到本地"""
    if not url:
        return None

    try:
        # 从URL中提取文件扩展名，处理掉可能的查询参数
        path = urlparse(url).path
        ext = os.path.splitext(path)[1]
        if not ext: # 如果没有扩展名，默认使用 .jpg
            ext = '.jpg'
            
        filename = f"{post_id}{ext}"
        filepath = os.path.join(IMAGE_OUTPUT_DIR, filename)

        # 发送请求下载图片
        img_response = requests.get(url, stream=True, timeout=20)
        img_response.raise_for_status()

        # 以二进制写模式保存图片文件
        with open(filepath, 'wb') as f:
            for chunk in img_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"🖼️  成功下载图片: {filepath}")
        return filepath # 返回本地文件路径
    except requests.RequestException as e:
        print(f"❌ 下载图片失败 {url}: {e}")
        return None
    except Exception as e:
        print(f"❌ 保存图片时出错: {e}")
        return None

def create_markdown_file(post_id, title, published_date, local_image_path, body_content, source_text):
    """根据提取的信息生成 Markdown 文件内容"""
    
    clean_title = title.replace("'", "’").replace('"', '”').strip()
    description = clean_title

    # 【修改点】根据本地图片路径生成相对路径
    image_frontmatter = "image: ''"
    if local_image_path:
        image_filename = os.path.basename(local_image_path)
        # 相对路径：从 posts/ -> ../ -> assets/images/
        relative_image_path = f"../assets/images/{image_filename}"
        image_frontmatter = f"image: '{relative_image_path}'"

    # 正文部分不再包含图片标签
    body_markdown = f"## {title}\n\n{body_content.strip()}\n\n"
    if source_text:
        body_markdown += f"*{source_text.strip()}*"

    content = f"""---
title: '{clean_title}'
published: {published_date}
description: '{description}'
{image_frontmatter}
tags: [科技频道]
category: '科技频道'
draft: false
lang: ''
---

{body_markdown}
"""
    
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
    
    # 【修改点】确保两个输出目录都存在
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

        # 提取图片 URL
        image_url = ''
        photo_wrap = widget_message.find('a', class_='tgme_widget_message_photo_wrap')
        if photo_wrap and 'style' in photo_wrap.attrs:
            match = re.search(r"url\('(.+?)'\)", photo_wrap['style'])
            if match:
                image_url = match.group(1)
        
        # 【修改点】下载图片并获取本地路径
        local_image_path = download_image(image_url, post_id)

        # 提取正文和来源... (逻辑不变)
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
        
        # 生成 Markdown 文件
        published_date = datetime.now().strftime('%Y-%m-%d')
        # 【修改点】传入本地图片路径
        create_markdown_file(post_id, title, published_date, local_image_path, body_content, source_text)

    if new_posts_count == 0:
        print("✅ 所有新闻都已是最新，无需更新。")
    else:
        print(f"🎉 处理完成，新增 {new_posts_count} 篇文章。")

if __name__ == "__main__":
    scrape_news()