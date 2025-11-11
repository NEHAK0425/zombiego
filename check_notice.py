import requests
from bs4 import BeautifulSoup
import json
import os

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1437840874204692540/DvTw1ozfe62zmMQ4cJmPK5rET5BysPR2c486yJMNv6GU6HUl09DDTIWho6V_HC_Znpja"

NOTICE_URL = "https://cafe.naver.com/f-e/cafes/27131930/menus/1?viewType=L"

STATE_FILE = "last_notice.json"

def get_latest_notice():
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(NOTICE_URL, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    # 공지 목록 중 첫 번째 글 찾기
    notice = soup.select_one(".article-board .td_article a")
    if not notice:
        return None

    title = notice.text.strip()
    link = "https://cafe.naver.com" + notice["href"]
    return {"title": title, "link": link}


def send_discord_message(title, link):
    data = {"content": f"📢 **새 공지 올라옴!**\n{title}\n{link}"}
    requests.post(DISCORD_WEBHOOK_URL, json=data)


def load_last_notice():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_last_notice(notice):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(notice, f, ensure_ascii=False, indent=2)


def main():
    latest = get_latest_notice()
    if not latest:
        print("❌ 공지를 찾지 못함")
        return

    last_notice = load_last_notice()

    if not last_notice or latest["link"] != last_notice.get("link"):
        print("📢 새 공지 발견!")
        send_discord_message(latest["title"], latest["link"])
        save_last_notice(latest)
    else:
        print("✅ 새 공지 없음")


if __name__ == "__main__":
    main()
