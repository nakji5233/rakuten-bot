import requests
import json
import tweepy
import random
import os  # クラウドの保管庫から鍵を取り出すための機能

# ==========================================
# 【設定エリア】鍵は「環境変数」から読み込みます
# ==========================================
# ※ここは書き換えないでください
APP_ID = os.environ.get("RAKUTEN_APP_ID")
AFFILIATE_ID = os.environ.get("RAKUTEN_AFFILIATE_ID")
API_KEY = os.environ.get("X_API_KEY")
API_SECRET = os.environ.get("X_API_SECRET")
ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("X_ACCESS_SECRET")

# ==========================================
# ロジック部分
# ==========================================

def get_furusato_items():
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"
    params = {
        "applicationId": APP_ID,
        "affiliateId": AFFILIATE_ID,
        "format": "json",
        "keyword": "ふるさと納税", 
        "genreId": 101381,
        "sort": "standard",
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        items = []
        for item in data['Items'][:20]:
            info = item['Item']
            try:
                price = int(info['itemPrice'])
            except:
                price = 0
            review_avg = info.get('reviewAverage', 0)
            review_count = info.get('reviewCount', 0)
            items.append({
                "title": info['itemName'],
                "price": price,
                "url": info['affiliateUrl'],
                "review_avg": review_avg,
                "review_count": review_count
            })
        return items
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def create_post_text(item):
    if not item: return None
    title = item['title']
    if len(title) > 35: title = title[:35] + "..."
    stars = "★" * int(item['review_avg'])
    text = f"""
{stars} {item['review_avg']} ({item['review_count']}件)
【ふるさと納税】評価の高い人気品！

{title}

💰寄付額: {item['price']:,}円

👇中身をチェックする
{item['url']}

#PR #ふるさと納税 #楽天マラソン #節税対策
"""
    return text.strip()

def post_to_x(text):
    client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )
    try:
        response = client.create_tweet(text=text)
        print(f"✅ Posted! ID: {response.data['id']}")
    except Exception as e:
        print(f"❌ Failed: {e}")

# --- メイン処理 ---
# scheduleやloopは削除しました。1回実行して終了します。
if __name__ == "__main__":
    print("🚀 Starting Bot...")
    items = get_furusato_items()
    if items:
        selected_item = random.choice(items)
        post_text = create_post_text(selected_item)
        post_to_x(post_text)
    else:
        print("⚠ No items found.")