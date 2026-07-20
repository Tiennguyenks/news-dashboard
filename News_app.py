import streamlit as st
import feedparser
import concurrent.futures
import re

# ==============================================================================
# CẤU HÌNH HỆ THỐNG
# ==============================================================================
# Danh sách nguồn tin RSS uy tín, cập nhật liên tục trong ngày
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

# ==============================================================================
# CÁC HÀM XỬ LÝ DỮ LIỆU
# ==============================================================================
def clean_html(raw_html):
    """Làm sạch các thẻ HTML thừa, loại bỏ ảnh lỗi trong phần mô tả của RSS"""
    if not raw_html:
        return "Bấm vào 'Xem bài gốc' để đọc chi tiết nội dung."
    # Xóa các thẻ HTML dạng <...>
    clean_text = re.sub('<[^<]+?>', '', raw_html)
    # Loại bỏ khoảng trắng thừa
    clean_text = clean_text.strip()
    if not clean_text:
        return "Bấm vào 'Xem bài gốc' để đọc chi tiết nội dung."
    return clean_text

def fetch_news_from_feed(feed_info, limit=8):
    """Đọc dữ liệu tin tức từ từng link RSS"""
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
    except Exception as e:
        return []

def get_all_news(feed_list):
    """Sử dụng đa luồng (Multi-threading) để tải nhiều báo cùng lúc vô cùng nhanh"""
    all_articles = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(lambda f: fetch_news_from_feed(f, limit=8), feed_list)
        for res in results:
            all_articles.extend(res)
    return all_articles

# ==============================================================================
# GIAO DIỆN DASHBOARD (STREAMLIT)
# ==============================================================================
st.set_page_config(page_title="Hệ thống Tổng hợp Tin tức Tự chủ", layout="wide")

# Tạo giao diện thẻ (Card) bằng CSS để các bài báo tách biệt, dễ đọc
st.markdown("""
    <style>
    .stApp { background-color: #f7f9fa; }
    .news-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #007bff;
        margin-bottom: 20px;
    }
    .news-card-global {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #28a745;
        margin-bottom: 20px;
    }
    .news-title { font-size: 18px; font-weight: bold; color: #111111; margin-bottom: 5px; }
    .news-meta { font-size: 13px; color: #6c757d; margin-bottom: 12px; }
    .news-summary { font-size: 15px; color: #333333; line-height: 1.5; }
    </style>
""", unsafe_allow_html=True)

st.title("📰 Daily News Dashboard")
st.caption("Hệ thống tự động tổng hợp tin tức trong ngày - Hoạt động độc lập, chi phí 0đ")

# Nút cập nhật thủ công
if st.button("🔄 Làm mới tin tức ngay"):
    st.cache_data.clear()

# Sử dụng bộ nhớ đệm ẩn để tránh tải lại dữ liệu liên tục khi người dùng cuộn trang
@st.cache_data(ttl=900) # Tự động làm mới sau mỗi 15 phút (900 giây)
def load_data():
    vn_raw = get_all_news(RSS_FEEDS["Trong nước"])
    world_raw = get_all_news(RSS_FEEDS["Thế giới"])
    return vn_raw, world_raw

with st.spinner("Đang kết nối nguồn tin và đồng bộ dữ liệu..."):
    vn_news, world_news = load_data()

# Chia bố cục giao diện làm 2 cột cân xứng
col1, col2 = st.columns(2)

with col1:
    st.markdown("## 🇻🇳 Tin tức Trong nước")
    st.write(f"Tìm thấy *{len(vn_news)}* tin tức mới cập nhật.")
    st.markdown("---")
    
    if not vn_news:
        st.info("Hiện tại chưa có tin mới hoặc lỗi kết nối nguồn tin quốc nội.")
    
    for idx, item in enumerate(vn_news):
        cleaned_desc = clean_html(item['summary'])
        
        # Hiển thị khối tin tức dạng hộp bằng HTML/CSS tùy biến
        st.markdown(f"""
            <div class="news-card">
                <div class="news-title">{idx+1}. {item['title']}</div>
                <div class="news-meta">Nguồn: {item['source']} | <a href="{item['link']}" target="_blank">Xem bài gốc ↗</a></div>
                <div class="news-summary">{cleaned_desc}</div>
            </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("## 🌐 Tin tức Quốc tế")
    st.write(f"Tìm thấy *{len(world_news)}* tin toàn cầu cập nhật.")
    st.markdown("---")
    
    if not world_news:
        st.info("Hiện tại chưa có tin mới hoặc lỗi kết nối nguồn tin thế giới.")
        
    for idx, item in enumerate(world_news):
        cleaned_desc = clean_html(item['summary'])
        
        st.markdown(f"""
            <div class="news-card-global">
                <div class="news-title">{idx+1}. {item['title']}</div>
                <div class="news-meta">Nguồn: {item['source']} | <a href="{item['link']}" target="_blank">Xem bài gốc ↗</a></div>
                <div class="news-summary">{cleaned_desc}</div>
            </div>
        """, unsafe_allow_html=True)