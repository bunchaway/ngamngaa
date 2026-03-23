import feedparser
import json
import datetime
from dateutil import parser # Thư viện giúp đọc mọi định dạng ngày tháng

def fetch_feeds():
    # 1. Đọc danh sách nguồn
    with open('sources.json', 'r', encoding='utf-8') as f:
        sources = json.load(f)

    all_items = []
    
    # 2. Tính toán ngày hôm nay và hôm qua
    now = datetime.datetime.now(datetime.timezone.utc)
    today = now.date()
    yesterday = today - datetime.timedelta(days=1)

    print(f"Chỉ lấy tin từ ngày: {yesterday} và {today}")

    # 3. Duyệt qua cấu trúc mới: type (learner/native) -> category (listening/reading) -> sub (youtube/...)
    for user_type, categories in sources.items():
        for category, sub_categories in categories.items():
            for sub_category, feeds in sub_categories.items():
                for feed in feeds:
                    print(f"Đang lấy tin từ: {feed['name']} ({user_type}/{category}/{sub_category})")
                    try:
                        d = feedparser.parse(feed['url'])
                        
                        for entry in d.entries[:15]: 
                            published_parsed = entry.get('published', entry.get('updated', None))
                            if published_parsed:
                                try:
                                    dt = parser.parse(published_parsed)
                                    # Chuyển về UTC
                                    if dt.tzinfo is None:
                                        dt = dt.replace(tzinfo=datetime.timezone.utc)
                                    else:
                                        dt = dt.astimezone(datetime.timezone.utc)
                                except:
                                    continue
                            else:
                                continue 
                            
                            # Kiểm tra ngày: chỉ lấy hôm nay và hôm qua
                            if dt.date() < yesterday:
                                continue

                            thumbnail = ""
                            if 'media_thumbnail' in entry:
                                thumbnail = entry.media_thumbnail[0]['url']
                            elif 'links' in entry:
                                for link in entry.links:
                                    if 'image' in link.get('rel', ''):
                                        thumbnail = link.href

                            item = {
                                "title": entry.title,
                                "link": entry.link,
                                "source": feed['name'],
                                "type": user_type,      # 'learner' or 'native'
                                "category": category,   # 'listening' or 'reading'
                                "sub": sub_category,    # 'youtube', 'podcast', 'reddit', 'other'
                                "date": dt.isoformat(),
                                "thumbnail": thumbnail,
                                "description": entry.get('summary', '')[:200] + '...'
                            }
                            all_items.append(item)
                    except Exception as e:
                        print(f"Lỗi tại {feed['name']}: {e}")

    # 4. Sắp xếp tất cả theo thời gian
    all_items.sort(key=lambda x: x['date'], reverse=True)

    # 5. Lưu kết quả
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print(f"Xong! Đã cập nhật {len(all_items)} nội dung vào data.json")

if __name__ == "__main__":
    fetch_feeds()