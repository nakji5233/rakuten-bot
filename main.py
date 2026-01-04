import requests
import json
import tweepy
import random
import os
import datetime

# ==========================================
# 【設定エリア】GitHubのSecretsから読み込み
# ==========================================
APP_ID = os.environ.get("RAKUTEN_APP_ID")
AFFILIATE_ID = os.environ.get("RAKUTEN_AFFILIATE_ID")
API_KEY = os.environ.get("X_API_KEY")
API_SECRET = os.environ.get("X_API_SECRET")
ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("X_ACCESS_SECRET")

# ==========================================
# 【戦略設定】1月〜2月に売れるキーワードリスト
# ==========================================
# Botはこの中からランダム、または時間帯で最適なものを選びます
TARGET_KEYWORDS = [
    {"keyword": "バレンタイン チョコ", "genreId": 0, "tag": "#バレンタイン #自分へのご褒美"},
    {"keyword": "訳あり スイーツ", "genreId": 0, "tag": "#訳あり #スイーツ部 #お取り寄せ"},
    {"keyword": "カニ 訳あり", "genreId": 0, "tag": "#カニ #鍋 #冬の味覚"},
    {"keyword": "入浴剤", "genreId": 0, "tag": "#入浴剤 #温活 #リラックス"},
    {"keyword": "電気毛布", "genreId": 0, "tag": "#節電 #寒さ対策 #暖房"},
    # ふるさと納税も少しだけ残しておく（完全に捨てるのはもったいないため）
    {"keyword": "ふるさと納税 先行予約", "genreId": 101381, "tag": "#ふるさと納税 #節税"},
]

# ==========================================
# ロジック部分
# ==========================================

def get_items(target):
    """
    指定されたターゲット（キーワード）で商品を検索
    """
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"
    
    params = {
        "applicationId": APP_ID,
        "affiliateId": AFFILIATE_ID,
        "format": "json",
        "keyword": target['keyword'],
        "genreId": target['genreId'],
        "sort": "standard", # 売れている順（標準）
        "hits": 30,         # 候補を多めに取得
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        items = []
        for item in data['Items']:
            info = item['Item']
            
            # レビュー件数が少ない（人気がない）商品は除外するフィルター
            # 品質向上のため、レビュー10件未満は無視
            if info.get('reviewCount', 0) < 10:
                continue

            try:
                price = int(info['itemPrice'])
            except:
                price = 0
            
            items.append({
                "title": info['itemName'],
                "price": price,
                "url": info['affiliateUrl'],
                "review_avg": info.get('reviewAverage', 0),
                "review_count": info.get('reviewCount', 0),
                "target_tag": target['tag'] # この商品のタグ情報を引き継ぐ
            })
        return items

    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def create_post_text(item):
    if not item: return None
    
    # タイトル調整（長すぎると見づらいため）
    title = item['title']
    if len(title) > 40: title = title[:40] + "..."
    
    # 星評価の視覚化
    stars = "★" * int(item['review_avg'])
    
    # 訴求文の作成
    # ユーザーの目を引くように「高評価」「限定感」を出す
    text = f"""
{stars} {item['review_avg']} (口コミ{item['review_count']}件)
話題の商品をピックアップ！✨

{title}

💰価格: {item['price']:,}円

👇詳細を見る
{item['url']}

{item['target_tag']} #楽天ROOM #ad
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
if __name__ == "__main__":
    print("🚀 Starting Bot (High Quality Mode)...")
    
    # 戦略リストからランダムに1つのテーマを選ぶ
    current_target = random.choice(TARGET_KEYWORDS)
    print(f"Targeting: {current_target['keyword']}")
    
    items = get_items(current_target)
    
    if items:
        # 取得したリストからランダムに1つ選ぶ
        selected_item = random.choice(items)
        post_text = create_post_text(selected_item)
        post_to_x(post_text)
    else:
        print("⚠ No suitable items found.")
