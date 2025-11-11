import requests
from bs4 import BeautifulSoup
import json
import os

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
LAST_NOTICE_FILE = "last_notice.json"

NOTICE_LIST_URL = "https://cafe.naver.com/ArticleList.nhn?search.clubid=27131930&search.menuid=1&search.boardtype=L"

def get_latest_notice():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(NOTICE_LIST_URL, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    notice_links = soup.select("a.article")
    if not notice_links:
        return None, None
    first_notice = notice_links[0]
    title = first_notice.text.strip()
    href = first_notice.get("href")
    full_link = f"https://cafe.naver.com{href}"
    return title, full_link

def load_last_notice():
    if os.path.exists(LAST_NOTICE_FILE):
        with open(LAST_NOTICE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"title": "", "link": ""}

def save_last_notice(title, link):
    with open(LAST_NOTICE_FILE, "w", encoding="utf-8") as f:
        json.dump({"title": title, "link": link}, f)

def send_discord_message(title, link):
    data = {"content": f"📢 새 공지가 올라왔어요!\n**{title}**\n👉 {link}"}
    requests.post(DISCORD_WEBHOOK_URL, json=data)

def main():
    last_notice = load_last_notice()
    title, link = get_latest_notice()
    if not title:
        print("공지 없음")
        return
    if title != last_notice["title"]:
        print("새 공지 발견:", title)
        send_discord_message(title, link)
        save_last_notice(title, link)
    else:
        print("새 공지 없음")

if __name__ == "__main__":
    main()
