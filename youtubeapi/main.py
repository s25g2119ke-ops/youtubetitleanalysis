import requests
from datetime import datetime, timezone, timedelta

API_KEY = "AIzaSyCc5rIrAAFsdBH0S4fCL1EOig5Oga7fsTA"
CHANNEL_ID = "UCp92fyjAf6AKqIwT036z5Zw"  

keyword = input("検索キーワード（空欄で全表示）: ").strip()
start_year = input("開始年（空欄で制限なし）: ").strip()
end_year = input("終了年（空欄で制限なし）: ").strip()

score_3 = [
    "全","大","絶","神","超","激","最","爆",
    "不可能","衝撃","ダントツ","鬼","死",
    "最強","最弱","最速","最悪",
    "神回","神引き","神展開","神性能",
    "爆死","爆勝","爆誕","爆速",
    "絶望","絶対",
    "覚醒","無双","チート",
    "壊れ","人権",
    "地獄","死亡","即死",
    "閲覧注意","放送事故",
    "世界一","日本一",
    "覇権","無敵",
    "禁断","終了",
    "サ終","引退","消えた"
]

score_2 = [
    "流行","話題","人気","注目",
    "ぶっ壊れ","炎上",
    "バズってる","伝説",
    "圧倒的","確定",
    "バズる","バズった",
    "確定演出",
    "新キャラ","新武器",
    "新環境","新作",
    "最新","アプデ",
    "大型アプデ",
    "検証","比較",
    "ランキング",
    "攻略","裏技",
    "秘密","極秘",
    "暴露","謝罪",
    "事件","奇跡",
    "無課金","課金",
    "100連","天井",
    "コンプ","完凸",
    "勝率100%",
    "連勝","MVP",
    "修正","ナーフ","バフ",
    "恐怖","ホラー",
    "トラウマ",
    "朗報","悲報"
]

score_1 = [
    "おすすめ",
    "解説",
    "初心者必見",
    "方法",
    "結論",
    "新",
    "実装",
    "解禁",
    "初公開",
    "ソロ",
    "初見",
    "24時間",
    "縛り",
    "耐久",
    "全クリ",
    "完全制覇",
    "稼ぎ",
    "効率",
    "最短",
    "周回",
    "レア",
    "先行公開",
    "修羅場",
    "泣いた",
    "笑った",
    "嘘だろ",
    "まさか",
    "ガチで",
    "ついに",
    "遂に",
    "なんと",
    "え？",
    "は？",
    "マジで"
]


def calculate_title_score(title):
    score = 0

    for word in score_3:
        if word in title:
            score += 3

    for word in score_2:
        if word in title:
            score += 2

    for word in score_1:
        if word in title:
            score += 1

    exclamations = title.count("!") + title.count("！")
    questions = title.count("?") + title.count("？")

    if 1 <= exclamations <= 5:
        score += 1
    elif exclamations > 5:
        score += 2

    if 1 <= questions <= 5:
        score += 1
    elif questions > 5:
        score += 2

    if (
        "!?" in title or
        "！？" in title or
        "⁉" in title
    ):
        score += 1

    return score


channel_url = "https://www.googleapis.com/youtube/v3/channels"

channel_params = {
    "part": "contentDetails",
    "id": CHANNEL_ID,
    "key": API_KEY
}

channel_data = requests.get(channel_url, params=channel_params).json()
uploads_playlist_id = channel_data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


playlist_url = "https://www.googleapis.com/youtube/v3/playlistItems"

video_ids = []
next_page_token = None

while True:
    playlist_params = {
        "part": "contentDetails",
        "playlistId": uploads_playlist_id,
        "maxResults": 50,
        "key": API_KEY
    }

    if next_page_token:
        playlist_params["pageToken"] = next_page_token

    playlist_data = requests.get(
        playlist_url,
        params=playlist_params
    ).json()

    for item in playlist_data["items"]:
        video_ids.append(item["contentDetails"]["videoId"])

    if "nextPageToken" not in playlist_data:
        break

    next_page_token = playlist_data["nextPageToken"]

print("取得動画総数:", len(video_ids))


videos_url = "https://www.googleapis.com/youtube/v3/videos"

count = 0
jst = timezone(timedelta(hours=9))
now = datetime.now(jst)

for i in range(0, len(video_ids), 50):
    batch_ids = ",".join(video_ids[i:i+50])

    video_params = {
        "part": "snippet,statistics",
        "id": batch_ids,
        "key": API_KEY
    }

    video_data = requests.get(videos_url, params=video_params).json()

    for item in video_data["items"]:
        title = item["snippet"]["title"]

        if keyword and keyword not in title:
            continue

        published_at = item["snippet"]["publishedAt"]

        utc_time = datetime.strptime(
            published_at,
            "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=timezone.utc)

        japan_time = utc_time.astimezone(jst)
        video_year = japan_time.year

        if start_year and video_year < int(start_year):
            continue

        if end_year and video_year > int(end_year):
            continue

        views = int(item["statistics"].get("viewCount", 0))
        comments = item["statistics"].get("commentCount", "コメント無効")

        days_passed = (now - japan_time).days

        if days_passed <= 0:
            avg_views_per_day = views
        else:
            avg_views_per_day = views / days_passed

        title_score = calculate_title_score(title)

        #print("----------------------")
        #print("タイトル:", title)
        #print(title_score)
        #print("投稿日:", japan_time.strftime("%Y-%m-%d %H:%M:%S"))
        #print("再生回数:", views)
        #print("コメント数:", comments)
        
        print(round(avg_views_per_day, 2))
    

        count += 1
    


print("----------------------")
print("条件に一致した動画数:", count)
