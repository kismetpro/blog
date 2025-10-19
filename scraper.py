import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# --- 配置 ---
# 目标 Telegram 频道网页
URL = "https://t.me/s/zaihuapd"
# Markdown 文件输出目录
OUTPUT_DIR = "src/content/posts"
# --- 结束配置 ---

def create_markdown_file(post_id, title, published_date, image_url, body_content, source_text):
    """根据提取的信息生成 Markdown 文件内容"""
    
    # 清理标题和描述中的特殊字符，避免在 frontmatter 中引起问题
    clean_title = title.replace("'", "’").replace('"', '”').strip()
    # 描述可以简单地使用标题
    description = clean_title

    # frontmatter 中的 image 字段，如果图片存在则填入 URL，否则为空
    image_frontmatter = f"image: '{image_url}'" if image_url else "image: ''"

    # 格式化正文
    # 【修改点】不再向正文中添加 ![alt](url) 图片标签
    body_markdown = ""
    body_markdown += f"## {title}\n\n"
    body_markdown += f"{body_content.strip()}\n\n"
    
    if source_text:
        # 如果来源文本存在，使用斜体格式化
        body_markdown += f"*{source_text.strip()}*"

    # 组装完整的 Markdown 文件内容
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
    
    # 定义文件名并保存
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
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(URL, headers=headers, timeout=20)
        response.raise_for_status()  # 如果请求失败则抛出异常
    except requests.RequestException as e:
        print(f"❌ 访问 {URL} 失败: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找所有新闻消息的容器
    messages = soup.find_all('div', class_='tgme_widget_message_wrap')
    
    if not messages:
        print("🟡 未找到任何新闻消息。")
        return

    print(f"🔍 找到 {len(messages)} 条消息，开始处理...")

    new_posts_count = 0
    for message_div in reversed(messages):  # 从旧到新处理，符合时间顺序
        widget_message = message_div.find('div', class_='js-widget_message')
        if not widget_message or 'data-post' not in widget_message.attrs:
            continue

        # 1. 判断新闻是否已被爬取
        post_id = widget_message['data-post'].split('/')[-1]
        filename = f"kjpd{post_id}.md"
        filepath = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(filepath):
            # print(f"⏭️ 跳过已存在的新闻: {post_id}")
            continue
        
        new_posts_count += 1
        print(f"🆕 发现新文章，ID: {post_id}")

        # 2. 提取新闻内容
        message_text_div = widget_message.find('div', class_='js-message_text')
        if not message_text_div:
            continue

        # 提取标题 (通常是第一个 <b> 标签)
        title_tag = message_text_div.find('b')
        title = title_tag.get_text(strip=True) if title_tag else f"无标题新闻 - {post_id}"

        # 提取图片 URL
        image_url = ''
        photo_wrap = widget_message.find('a', class_='tgme_widget_message_photo_wrap')
        if photo_wrap and 'style' in photo_wrap.attrs:
            style = photo_wrap['style']
            match = re.search(r"url\('(.+?)'\)", style)
            if match:
                image_url = match.group(1)

        # 提取正文和来源
        # 复制一份用于操作，避免破坏原始结构
        content_soup = BeautifulSoup(str(message_text_div), 'html.parser')
        
        # 移除标题 <b>
        if content_soup.b:
            content_soup.b.decompose()
        
        # 查找来源链接 (最后一个不是 Telegram 内部链接的 a 标签)
        source_text = ''
        all_links = content_soup.find_all('a')
        source_link_tag = None
        for link in reversed(all_links):
            href = link.get('href', '')
            if 't.me/' not in href:
                source_text = link.get_text(strip=True)
                source_link_tag = link
                break
        
        # 移除所有链接和频道固定页脚，以获得纯净的正文
        for tag in content_soup.find_all(['a', 'i']):
            tag.decompose()
            
        # 移除特定文本模式的页脚（例如群友投稿补充）
        body_content = content_soup.get_text(separator='\n', strip=True)
        body_content = re.sub(r'群友投稿补充\s*', '', body_content) # 移除群友投稿提示
        
        # 3. 生成 Markdown 文件
        published_date = datetime.now().strftime('%Y-%m-%d')
        create_markdown_file(post_id, title, published_date, image_url, body_content, source_text)

    if new_posts_count == 0:
        print("✅ 所有新闻都已是最新，无需更新。")
    else:
        print(f"🎉 处理完成，新增 {new_posts_count} 篇文章。")


if __name__ == "__main__":
    scrape_news()