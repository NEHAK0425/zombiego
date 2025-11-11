import requests
from bs4 import BeautifulSoup
import json
import os

# 네이버 카페 공지 URL
NOTICE_URL = "https://cafe.naver.com/f-e/cafes/27131930/menus/1?viewType=L"
LAST_NOTICE_FILE = "last_notice.json"

# Discord 웹훅 URL (GitHub Secrets에서 불러옴)
DISCORD_WEBHOOK = os.getenv("https://discord.com/api/webhooks/1437840874204692540/DvTw1ozfe62zmMQ4cJmPK5rET5BysPR2c486yJMNv6GU6HUl09DDTIWho6V_HC_Znpja")

def get_latest_notice():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(NOTICE_URL, headers=headers)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    # 공지 목록에서 첫 번째 항목 추출
    notice_el = soup.select_one(".article-board .board-list .board-notice a")
    if not notice_el:
        return None

    title = notice_el.get_text(strip=True)
    link = "https://cafe.naver.com" + notice_el["href"]
    return {"title": title, "link": link}

def load_last_notice():
    if os.path.exists(LAST_NOTICE_FILE):
        with open(LAST_NOTICE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_last_notice(notice):
    with open(LAST_NOTICE_FILE, "w", encoding="utf-8") as f:
        json.dump(notice, f, ensure_ascii=False, indent=2)

def send_to_discord(notice):
    if not DISCORD_WEBHOOK:
        print("❌ Discord 웹훅 URL이 설정되지 않았습니다.")
        return
    data = {
        "content": f"📢 **새 공지 올라왔어요!**\n\n📰 {notice['title']}\n🔗 {notice['link']}"
    }
    res = requests.post(DISCORD_WEBHOOK, json=data)
    if res.status_code == 204:
        print("✅ Discord 알림 전송 완료!")
    else:
        print(f"⚠️ 전송 실패 ({res.status_code}): {res.text}")

def main():
    latest = get_latest_notice()
    if not latest:
        print("공지 정보를 불러올 수 없습니다.")
        return

    last = load_last_notice()
    if last and latest["title"] == last.get("title"):
        print("새 공지가 없습니다.")
        return

    send_to_discord(latest)
    save_last_notice(latest)

if __name__ == "__main__":
    main()

