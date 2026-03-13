import feedparser
import json
import datetime
from dateutil import parser # Thư viện giúp đọc mọi định dạng ngày tháng

def fetch_feeds():
    # 1. Đọc danh sách nguồn từ Bước 1
    with open('sources.json', 'r', encoding='utf-8') as f:
        sources = json.load(f)

    all_items = []

    # 2. Duyệt qua từng Level và Category
    for level, categories in sources.items():
        for category, feeds in categories.items():
            for feed in feeds:
                print(f"Đang lấy tin từ: {feed['name']} ({level})")
                try:
                    # Dùng feedparser để đọc nội dung RSS
                    d = feedparser.parse(feed['url'])
                    
                    for entry in d.entries[:10]: # Lấy 10 tin mới nhất mỗi nguồn
                        # Chuẩn hóa ngày tháng để sắp xếp Timeline
                        published_parsed = entry.get('published', entry.get('updated', None))
                        if published_parsed:
                            dt = parser.parse(published_parsed)
                        else:
                            dt = datetime.datetime.now()

                        item = {
                            "title": entry.title,
                            "link": entry.link,
                            "source": feed['name'],
                            "level": level,
                            "category": category,
                            "date": dt.isoformat(),
                            "description": entry.get('summary', '')[:200] + '...' # Cắt ngắn mô tả
                        }
                        all_items.append(item)
                except Exception as e:
                    print(f"Lỗi tại {feed['name']}: {e}")

    # 3. Sắp xếp tất cả theo thời gian (Mới nhất lên đầu)
    all_items.sort(key=lambda x: x['date'], reverse=True)

    # 4. Lưu kết quả ra file data.json để Web sử dụng
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print(f"Xong! Đã cập nhật {len(all_items)} nội dung vào data.json")

if __name__ == "__main__":
    fetch_feeds()