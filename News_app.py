import streamlit as st
import feedparser
import concurrent.futures
import re

# ==============================================================================
# CẤU HÌNH HỆ THỐNG & NGUỒN TIN
# ==============================================================================
# Nguồn RSS tin tức
RSS_FEEDS = {
    "Trong nước": [
        {"name": "VnExpress - Thời sự", "url": "https://vnexpress.net/rss/thoi-su.rss"},
        {"name": "Tuổi Trẻ - Thế giới", "url": "https://tuoitre.vn/rss/the-gioi.rss"},
        {"name": "VietNamNet - Thời sự", "url": "https://vietnamnet.vn/rss/thoi-su.rss"}
    ],
    "Thế giới": [
        {"name": "Reuters - World", "url": "https://news.google.com/rss/search?q=when:1d+source:Reuters&hl=en-US&gl=US&ceid=US:en"},
        {"name": "BBC News - World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
        {"name": "CNN - Top Stories", "url": "http://rss.cnn.com/rss/edition.rss"}
    ]
}

# Nguồn tin tức riêng về Thị trường & Giá vàng
GOLD_NEWS_FEED = "https://vnexpress.net/rss/kinh-doanh.rss"

# ==============================================================================
# CÁC HÀM XỬ LÝ DỮ LIỆU
# ==============================================================================
def clean_html(raw_html):
    """Làm sạch mã HTML thừa trong văn bản RSS"""
    if not raw_html:
        return "Bấm vào 'Xem bài gốc' để xem chi tiết."
    clean_text = re.sub('<[^<]+?>', '', raw_html).strip()
    return clean_text if clean_text else "Bấm vào 'Xem bài gốc' để xem chi tiết."

def fetch_news_from_feed(feed_info, limit=8):
    """Lấy tin tức từ 1 nguồn RSS"""
    try:
        feed = feedparser.parse(feed_info["url"])
        articles = []
        for entry in feed.entries[:limit]:
            articles.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "source": feed_info["name"]
            })
        return articles
    except Exception:
        return []

def get_all_news(feed_list):
    """Lấy tin tức đa luồng siêu tốc"""
    all_articles = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(lambda f: fetch_news_from_feed(f, limit=8), feed_list)
        for res in results:
            all_articles.extend(res)
    return all_articles

def fetch_gold_trends():
    """Lọc các bài tin liên quan đến Giá vàng để phân tích xu hướng"""
    try:
        feed = feedparser.parse(GOLD_NEWS_FEED)
        gold_articles = []
        keywords = ["giá vàng", "vàng sjc", "vàng nhẫn", "gold price", "giá vàng hôm nay"]
        
        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            full_text = f"{title} {summary}".lower()
            
            # Kiểm tra xem bài báo có chứa từ khóa về giá vàng không
            if any(kw in full_text for kw in keywords):
                # Phân tích xu hướng dựa trên từ khóa trong tiêu đề
                trend = "TRUNG LẬP"
                trend_color = "#6c757d"
                if any(word in full_text for word in ["tăng", "lập đỉnh", "vọt", "bật tăng", "vượt"]):
                    trend = "TĂNG 🔺"
                    trend_color = "#28a745"
                elif any(word in full_text for word in ["giảm", "lao dốc", "tụt", "rớt", "bốc hơi"]):
                    trend = "GIẢM 🔻"
                    trend_color = "#dc3545"
                    
                gold_articles.append({
                    "title": title,
                    "link": entry.get("link", ""),
                    "summary": clean_html(summary),
                    "trend": trend,
                    "trend_color": trend_color
                })
        return gold_articles[:3] # Lấy 3 tin mới nhất về vàng
    except Exception:
        return []

# ==============================================================================
# GIAO DIỆN DASHBOARD (STREAMLIT)
# ==============================================================================
st.set_page_config(page_title="Daily News & Gold Dashboard", layout="wide")

# Cấu hình CSS tùy biến giao diện
st.markdown("""
    <style>
    .stApp { background-color: #f7f9fa; }
    .gold-box {
        background-color: #fff8e1;
        padding: 15px 20px;
        border-radius: 10px;
        border-left: 6px solid #ffc107;
        margin-bottom: 25px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .news-card {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #007bff;
        margin-bottom: 18px;
    }
    .news-card-global {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #28a745;
        margin-bottom: 18px;
    }
    .news-title { font-size: 17px; font-weight: bold; color: #111111; margin-bottom: 6px; }
    .news-meta { font-size: 13px; color: #6c757d; margin-bottom: 10px; }
    .news-summary { font-size: 14px; color: #333333; line-height: 1.5; }
    .trend-badge {
        display: inline-block;
        padding: 3px 8px;
        font-size: 12px;
        font-weight: bold;
        color: white;
        border-radius: 4px;
        margin-left: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📰 Daily News & Financial Dashboard")
st.caption("Tự động tổng hợp Tin tức & Xu hướng Giá vàng trong ngày - Chi phí 0đ")

# Nút cập nhật
if st.button("🔄 Cập nhật dữ liệu ngay"):
    st.cache_data.clear()

@st.cache_data(ttl=900) # Lưu bộ nhớ đệm 15 phút
def load_all_data():
    vn_raw = get_all_news(RSS_FEEDS["Trong nước"])
    world_raw = get_all_news(RSS_FEEDS["Thế giới"])
    gold_data = fetch_gold_trends()
    return vn_raw, world_raw, gold_data

with st.spinner("Đang tải tin tức và phân tích biến động thị trường..."):
    vn_news, world_news, gold_news = load_all_data()

# ==============================================================================
# PHẦN 1: TỔNG HỢP XU HƯỚNG GIÁ VÀNG
# ==============================================================================
st.markdown("### 🟡 Xu hướng & Biến động Giá vàng hôm nay")

if gold_news:
    gold_cols = st.columns(len(gold_news))
    for i, g_item in enumerate(gold_news):
        with gold_cols[i]:
            st.markdown(f"""
                <div class="gold-box">
                    <span style="font-size: 12px; color: #856404; font-weight: bold;">TIN THỊ TRƯỜNG</span>
                    <span class="trend-badge" style="background-color: {g_item['trend_color']};">{g_item['trend']}</span>
                    <div style="font-size: 15px; font-weight: bold; margin-top: 8px; color: #212529;">
                        {g_item['title']}
                    </div>
                    <div style="font-size: 13px; color: #555; margin-top: 6px; line-height: 1.4;">
                        {g_item['summary'][:130]}...
                    </div>
                    <div style="margin-top: 8px; font-size: 12px;">
                        <a href="{g_item['link']}" target="_blank">Đọc phân tích chi tiết ↗</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
else:
    st.info("Chưa tìm thấy bài viết phân tích giá vàng mới trong vài giờ qua.")

st.markdown("---")

# ==============================================================================
# PHẦN 2: TIN TỨC TRONG NƯỚC & QUỐC TẾ
# ==============================================================================
col1, col2 = st.columns(2)

with col1:
    st.markdown("## 🇻🇳 Tin tức Trong nước")
    st.write(f"Cập nhật *{len(vn_news)}* tin tức mới nhất.")
    
    for idx, item in enumerate(vn_news):
        st.markdown(f"""
            <div class="news-card">
                <div class="news-title">{idx+1}. {item['title']}</div>
                <div class="news-meta">Nguồn: {item['source']} | <a href="{item['link']}" target="_blank">Xem bài gốc ↗</a></div>
                <div class="news-summary">{clean_html(item['summary'])}</div>
            </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("## 🌐 Tin tức Quốc tế")
    st.write(f"Cập nhật *{len(world_news)}* tin tức toàn cầu.")
    
    for idx, item in enumerate(world_news):
        st.markdown(f"""
            <div class="news-card-global">
                <div class="news-title">{idx+1}. {item['title']}</div>
                <div class="news-meta">Nguồn: {item['source']} | <a href="{item['link']}" target="_blank">Xem bài gốc ↗</a></div>
                <div class="news-summary">{clean_html(item['summary'])}</div>
            </div>
        """, unsafe_allow_html=True)
