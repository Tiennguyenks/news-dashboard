import streamlit as st
import feedparser
import concurrent.futures
import re
import plotly.express as px
import pandas as pd

# ==============================================================================
# CẤU HÌNH HỆ THỐNG & DỰA TRÊN DÂNHMỤC NGUỒN TIN DÀNH CHO BẠN
# ==============================================================================
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
    ],
    "Công nghệ & Năng lượng": [
        {"name": "VnExpress - Khoa học Công nghệ", "url": "https://vnexpress.net/rss/khoa-hoc.rss"},
        {"name": "VietNamNet - Công nghệ", "url": "https://vietnamnet.vn/rss/cong-nghe.rss"},
        {"name": "Google News - Năng lượng & BESS", "url": "https://news.google.com/rss/search?q=renewable+energy+OR+BESS+OR+energy+storage+OR+battery+when:1d&hl=en-US&gl=US&ceid=US:en"}
    ],
    "Thị trường & Trung Quốc": [
        {"name": "VnExpress - Kinh doanh", "url": "https://vnexpress.net/rss/kinh-doanh.rss"},
        {"name": "Google News - Xu hướng Trung Quốc", "url": "https://news.google.com/rss/search?q=China+tech+OR+China+export+OR+China+manufacturing+when:1d&hl=en-US&gl=US&ceid=US:en"}
    ]
}

GOLD_NEWS_FEED = "https://vnexpress.net/rss/kinh-doanh.rss"

# ==============================================================================
# CÁC HÀM XỬ LÝ DỮ LIỆU & PHÂN LOẠI CHUYÊN SÂU
# ==============================================================================
def clean_html(raw_html):
    if not raw_html:
        return ""
    return re.sub('<[^<]+?>', '', raw_html).strip()

def generate_bullet_summary(text, max_bullets=2):
    cleaned = clean_html(text)
    if not cleaned:
        return "• Bấm vào 'Xem bài gốc' để xem chi tiết."
    
    sentences = [s.strip() for s in re.split(r'\.|\?|\!', cleaned) if len(s.strip()) > 15]
    if not sentences:
        return f"• {cleaned[:120]}..."
    
    bullets = [f"• {s}." for s in sentences[:max_bullets]]
    return "\n".join(bullets)

def fetch_news_from_feed(feed_info, limit=6):
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
    all_articles = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(lambda f: fetch_news_from_feed(f, limit=6), feed_list)
        for res in results:
            all_articles.extend(res)
    return all_articles

def fetch_gold_trends():
    try:
        feed = feedparser.parse(GOLD_NEWS_FEED)
        gold_articles = []
        keywords = ["giá vàng", "vàng sjc", "vàng nhẫn", "gold price", "giá vàng hôm nay"]
        
        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            full_text = f"{title} {summary}".lower()
            
            if any(kw in full_text for kw in keywords):
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
                    "summary": summary,
                    "trend": trend,
                    "trend_color": trend_color
                })
        return gold_articles
    except Exception:
        return []

# Filter lọc chủ đề chuyên sâu
def filter_specialized_news(articles, keywords):
    filtered = []
    for item in articles:
        full_text = f"{item['title']} {item['summary']}".lower()
        if any(kw.lower() in full_text for kw in keywords):
            filtered.append(item)
    return filtered

# ==============================================================================
# GIAO DIỆN DASHBOARD (STREAMLIT)
# ==============================================================================
st.set_page_config(page_title="Visual Daily News & Industry Dashboard", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .gold-box {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 10px;
        border-top: 4px solid #ffc107;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .news-card {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border-left: 4px solid #0d6efd;
        margin-bottom: 16px;
    }
    .news-card-global {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border-left: 4px solid #198754;
        margin-bottom: 16px;
    }
    .news-card-tech {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border-left: 4px solid #6f42c1;
        margin-bottom: 16px;
    }
    .news-title { font-size: 15.5px; font-weight: bold; color: #212529; margin-bottom: 6px; }
    .news-meta { font-size: 12px; color: #6c757d; margin-bottom: 10px; }
    .bullet-summary { 
        background-color: #f1f3f5; 
        padding: 10px 14px; 
        border-radius: 6px; 
        font-size: 13.5px; 
        color: #343a40;
        line-height: 1.6;
    }
    .trend-badge {
        display: inline-block;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: bold;
        color: white;
        border-radius: 4px;
    }
    .footer {
        text-align: center;
        padding: 20px;
        font-size: 14px;
        color: #6c757d;
        margin-top: 30px;
        border-top: 1px solid #e9ecef;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Daily News & Industry Trends Dashboard")
st.caption("🚀 Hệ thống tổng hợp, Trực quan hóa Tin tức & Xu hướng Ngành | **Nội dung được tạo bởi tiennguyenks**")

if st.button("🔄 Cập nhật dữ liệu ngay"):
    st.cache_data.clear()

@st.cache_data(ttl=900)
def load_all_data():
    vn_raw = get_all_news(RSS_FEEDS["Trong nước"])
    world_raw = get_all_news(RSS_FEEDS["Thế giới"])
    tech_raw = get_all_news(RSS_FEEDS["Công nghệ & Năng lượng"])
    market_raw = get_all_news(RSS_FEEDS["Thị trường & Trung Quốc"])
    gold_data = fetch_gold_trends()
    return vn_raw, world_raw, tech_raw, market_raw, gold_data

with st.spinner("Đang kết nối nguồn tin kỹ thuật, năng lượng và thị trường..."):
    vn_news, world_news, tech_news, market_news, gold_news = load_all_data()

# Lọc tin chuyên ngành
energy_bess_news = filter_specialized_news(
    tech_news + world_news + vn_news, 
    ["năng lượng", "bess", "pin", "nguồn điện", "điện gió", "mặt trời", "renewable", "battery", "grid", "trạm biến áp", "lưới điện", "power"]
)

china_biz_news = filter_specialized_news(
    market_news + world_news, 
    ["trung quốc", "china", "xuất khẩu", "kinh doanh", "mặt hàng", "sản xuất", "chuỗi cung ứng", "xu hướng", "thị trường"]
)

# ==============================================================================
# PHẦN 1: TỔNG QUAN VÀ BIỂU ĐỒ TRỰC QUAN
# ==============================================================================
st.markdown("### 📈 Tổng quan Chỉ số & Phân tích Thị trường")

trend_counts = {"TĂNG 🔺": 0, "GIẢM 🔻": 0, "TRUNG LẬP": 0}
for item in gold_news:
    trend_counts[item["trend"]] += 1

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Tin trong nước", f"{len(vn_news)} bài")
m2.metric("Tin quốc tế", f"{len(world_news)} bài")
m3.metric("Năng lượng & BESS", f"{len(energy_bess_news)} tin")
m4.metric("Thị trường/TQ", f"{len(china_biz_news)} tin")
m5.metric("Xu hướng Vàng", max(trend_counts, key=trend_counts.get) if gold_news else "N/A")

st.markdown("---")

col_chart, col_gold = st.columns([1, 1.8])

with col_chart:
    st.markdown("##### 🟡 Biểu đồ Tỷ lệ Xu hướng Giá vàng")
    if gold_news:
        df_chart = pd.DataFrame(list(trend_counts.items()), columns=['Xu hướng', 'Số lượng'])
        fig = px.pie(
            df_chart, 
            values='Số lượng', 
            names='Xu hướng', 
            hole=0.5,
            color='Xu hướng',
            color_discrete_map={'TĂNG 🔺': '#28a745', 'GIẢM 🔻': '#dc3545', 'TRUNG LẬP': '#6c757d'}
        )
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=220)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Chưa đủ dữ liệu để vẽ biểu đồ xu hướng.")

with col_gold:
    st.markdown("##### 📰 Bài viết Phân tích Giá vàng Mới nhất")
    if gold_news:
        for g_item in gold_news[:2]:
            st.markdown(f"""
                <div class="gold-box">
                    <span class="trend-badge" style="background-color: {g_item['trend_color']};">{g_item['trend']}</span>
                    <strong style="font-size: 14px; margin-left: 6px;">{g_item['title']}</strong>
                    <div class="bullet-summary" style="margin-top: 8px;">
                        {generate_bullet_summary(g_item['summary'])}
                    </div>
                    <div style="margin-top: 6px; font-size: 11px;">
                        <a href="{g_item['link']}" target="_blank">Đọc bài gốc ↗</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# ==============================================================================
# PHẦN 2: CHUYÊN MỤC CÔNG NGHỆ, NĂNG LƯỢNG TÁI TẠO, BESS & THỊ TRƯỜNG TRUNG QUỐC
# ==============================================================================
st.markdown("### ⚡ Công nghệ mới, Năng lượng tái tạo, BESS & Xu thế Thị trường")

tab1, tab2 = st.tabs(["🔋 Năng lượng tái tạo, BESS & Nguồn điện", "🇨🇳 Xu thế Kinh doanh & Mặt hàng mới từ Trung Quốc"])

with tab1:
    if energy_bess_news:
        cols = st.columns(2)
        for idx, item in enumerate(energy_bess_news[:6]):
            col_idx = idx % 2
            with cols[col_idx]:
                bullet_text = generate_bullet_summary(item['summary'])
                st.markdown(f"""
                    <div class="news-card-tech">
                        <div class="news-title">⚡ {item['title']}</div>
                        <div class="news-meta">Nguồn: {item['source']} | <a href="{item['link']}" target="_blank">Xem bài gốc ↗</a></div>
                        <div class="bullet-summary">
                            <b>📌 Điểm tin cốt lõi:</b><br>
                            {bullet_text.replace('\n', '<br>')}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Chưa tìm thấy tin tức mới phát sinh về Năng lượng tái tạo/BESS trong vài giờ qua.")

with tab2:
    if china_biz_news:
        cols = st.columns(2)
        for idx, item in enumerate(china_biz_news[:6]):
            col_idx = idx % 2
            with cols[col_idx]:
                bullet_text = generate_bullet_summary(item['summary'])
                st.markdown(f"""
                    <div class="news-card-tech">
                        <div class="news-title">📦 {item['title']}</div>
                        <div class="news-meta">Nguồn: {item['source']} | <a href="{item['link']}" target="_blank">Xem bài gốc ↗</a></div>
                        <div class="bullet-summary">
                            <b>📌 Điểm tin cốt lõi:</b><br>
                            {bullet_text.replace('\n', '<br>')}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Chưa tìm thấy tin tức mới về Thị trường & Mặt hàng Trung Quốc.")

st.markdown("---")

# ==============================================================================
# PHẦN 3: TIN TỨC TRONG NƯỚC & QUỐC TẾ
# ==============================================================================
col1, col2 = st.columns(2)

with col1:
    st.markdown("## 🇻🇳 Tin tức Trong nước")
    
    for idx, item in enumerate(vn_news[:6]):
        bullet_text = generate_bullet_summary(item['summary'])
        st.markdown(f"""
            <div class="news-card">
                <div class="news-title">{idx+1}. {item['title']}</div>
                <div class="news-meta">Nguồn: {item['source']} | <a href="{item['link']}" target="_blank">Xem bài gốc ↗</a></div>
                <div class="bullet-summary">
                    <b>📌 Tóm tắt nhanh:</b><br>
                    {bullet_text.replace('\n', '<br>')}
                </div>
            </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("## 🌐 Tin tức Quốc tế")
    
    for idx, item in enumerate(world_news[:6]):
        bullet_text = generate_bullet_summary(item['summary'])
        st.markdown(f"""
            <div class="news-card-global">
                <div class="news-title">{idx+1}. {item['title']}</div>
                <div class="news-meta">Nguồn: {item['source']} | <a href="{item['link']}" target="_blank">Xem bài gốc ↗</a></div>
                <div class="bullet-summary">
                    <b>📌 Tóm tắt nhanh:</b><br>
                    {bullet_text.replace('\n', '<br>')}
                </div>
            </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# CHÂN TRANG (FOOTER)
# ==============================================================================
st.markdown("""
    <div class="footer">
        © Daily News & Financial Dashboard | <strong>Nội dung được tạo bởi tiennguyenks</strong>
    </div>
""", unsafe_allow_html=True)
