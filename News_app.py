import streamlit as st
import feedparser
import concurrent.futures
import re
import plotly.express as px
import pandas as pd

# ==============================================================================
# CẤU HÌNH ĐA NGÔN NGỮ (DICTIONARY TRANSLATIONS)
# ==============================================================================
LANG_TEXT = {
    "VI": {
        "page_title": "Visual Daily News & Industry Dashboard",
        "title": "📊 Daily News & Industry Trends Dashboard",
        "author": "Nội dung được tạo bởi tiennguyenks",
        "btn_refresh": "🔄 Cập nhật dữ liệu ngay",
        "spinner": "Đang kết nối nguồn tin kỹ thuật, năng lượng và thị trường...",
        "sec_overview": "📈 Tổng quan Chỉ số & Phân tích Thị trường",
        "metric_vn": "Tin trong nước",
        "metric_world": "Tin quốc tế",
        "metric_energy": "Năng lượng & BESS",
        "metric_market": "Thị trường / Trung Quốc",
        "metric_gold_trend": "Xu hướng Vàng",
        "chart_title": "🟡 Biểu đồ Tỷ lệ Xu hướng Giá vàng",
        "chart_no_data": "Chưa đủ dữ liệu để vẽ biểu đồ xu hướng.",
        "gold_articles_title": "📰 Bài viết Phân tích Giá vàng Mới nhất",
        "read_original": "Đọc bài gốc ↗",
        "summary_label": "📌 Điểm tin cốt lõi:",
        "sec_specialized": "⚡ Công nghệ mới, Năng lượng tái tạo, BESS & Xu thế Thị trường",
        "tab_energy": "🔋 Năng lượng tái tạo, BESS & Nguồn điện",
        "tab_china": "🇨🇳 Xu thế Kinh doanh & Mặt hàng mới từ Trung Quốc",
        "no_energy_news": "Chưa tìm thấy tin tức mới phát sinh về Năng lượng tái tạo/BESS.",
        "no_china_news": "Chưa tìm thấy tin tức mới về Thị trường & Mặt hàng Trung Quốc.",
        "sec_vn_news": "🇻🇳 Tin tức Trong nước",
        "sec_world_news": "🌐 Tin tức Quốc tế",
        "trend_up": "TĂNG 🔺",
        "trend_down": "GIẢM 🔻",
        "trend_neutral": "TRUNG LẬP",
        "select_lang": "🌐 Chọn ngôn ngữ / Choose language:"
    },
    "EN": {
        "page_title": "Visual Daily News & Industry Dashboard",
        "title": "📊 Daily News & Industry Trends Dashboard",
        "author": "Content created by tiennguyenks",
        "btn_refresh": "🔄 Refresh Data Now",
        "spinner": "Fetching technical, energy, and market feeds...",
        "sec_overview": "📈 Market Indicators & Overview",
        "metric_vn": "Domestic News",
        "metric_world": "Global News",
        "metric_energy": "Energy & BESS",
        "metric_market": "Market / China",
        "metric_gold_trend": "Gold Trend",
        "chart_title": "🟡 Gold Price Trend Share",
        "chart_no_data": "Not enough data for trend chart.",
        "gold_articles_title": "📰 Latest Gold Analysis Articles",
        "read_original": "Read full story ↗",
        "summary_label": "📌 Key Takeaways:",
        "sec_specialized": "⚡ Tech, Renewable Energy, BESS & Market Trends",
        "tab_energy": "🔋 Renewable Energy, BESS & Power Grid",
        "tab_china": "🇨🇳 Business Trends & China Commodities",
        "no_energy_news": "No new updates on Renewable Energy/BESS at the moment.",
        "no_china_news": "No new updates on China Market/Commodities at the moment.",
        "sec_vn_news": "🇻🇳 Domestic News",
        "sec_world_news": "🌐 World News",
        "trend_up": "UP 🔺",
        "trend_down": "DOWN 🔻",
        "trend_neutral": "NEUTRAL",
        "select_lang": "🌐 Choose language / Chọn ngôn ngữ:"
    }
}

# ==============================================================================
# CẤU HÌNH RSS FEEDS THEO NGÔN NGỮ
# ==============================================================================
RSS_FEEDS_CONFIG = {
    "VI": {
        "Trong nước": [
            {"name": "VnExpress - Thời sự", "url": "https://vnexpress.net/rss/thoi-su.rss"},
            {"name": "Tuổi Trẻ - Thế giới", "url": "https://tuoitre.vn/rss/the-gioi.rss"},
            {"name": "VietNamNet - Thời sự", "url": "https://vietnamnet.vn/rss/thoi-su.rss"}
        ],
        "Thế giới": [
            {"name": "Reuters - World", "url": "https://news.google.com/rss/search?q=when:1d+source:Reuters&hl=en-US&gl=US&ceid=US:en"},
            {"name": "BBC News - World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"}
        ],
        "Công nghệ & Năng lượng": [
            {"name": "VnExpress - Khoa học", "url": "https://vnexpress.net/rss/khoa-hoc.rss"},
            {"name": "VietNamNet - Công nghệ", "url": "https://vietnamnet.vn/rss/cong-nghe.rss"},
            {"name": "Google News - BESS & Renewable", "url": "https://news.google.com/rss/search?q=renewable+energy+OR+BESS+OR+energy+storage+when:1d&hl=vi&gl=VN&ceid=VN:vi"}
        ],
        "Thị trường & Trung Quốc": [
            {"name": "VnExpress - Kinh doanh", "url": "https://vnexpress.net/rss/kinh-doanh.rss"},
            {"name": "Google News - Xu hướng Trung Quốc", "url": "https://news.google.com/rss/search?q=Trung+Quốc+xuất+khẩu+OR+công+nghệ+when:1d&hl=vi&gl=VN&ceid=VN:vi"}
        ]
    },
    "EN": {
        "Trong nước": [
            {"name": "VnExpress International", "url": "https://e.vnexpress.net/rss/news.rss"},
            {"name": "VietNamNet Global", "url": "https://vietnamnet.vn/rss/english.rss"}
        ],
        "Thế giới": [
            {"name": "Reuters World", "url": "https://news.google.com/rss/search?q=when:1d+source:Reuters&hl=en-US&gl=US&ceid=US:en"},
            {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"}
        ],
        "Công nghệ & Năng lượng": [
            {"name": "Google News - BESS & Renewable Energy", "url": "https://news.google.com/rss/search?q=renewable+energy+OR+BESS+OR+battery+storage+OR+power+grid+when:1d&hl=en-US&gl=US&ceid=US:en"}
        ],
        "Thị trường & Trung Quốc": [
            {"name": "Google News - China Tech & Export", "url": "https://news.google.com/rss/search?q=China+tech+OR+China+export+OR+China+manufacturing+when:1d&hl=en-US&gl=US&ceid=US:en"}
        ]
    }
}

GOLD_NEWS_FEED = "https://vnexpress.net/rss/kinh-doanh.rss"

# ==============================================================================
# HÀM XỬ LÝ DỮ LIỆU
# ==============================================================================
def clean_html(raw_html):
    if not raw_html:
        return ""
    return re.sub('<[^<]+?>', '', raw_html).strip()

def generate_bullet_summary(text, max_bullets=2):
    cleaned = clean_html(text)
    if not cleaned:
        return "• Click 'Read original' for full details."
    
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

def fetch_gold_trends(lang_code="VI"):
    t = LANG_TEXT[lang_code]
    try:
        feed = feedparser.parse(GOLD_NEWS_FEED)
        gold_articles = []
        keywords = ["giá vàng", "vàng sjc", "vàng nhẫn", "gold price", "gold"]
        
        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            full_text = f"{title} {summary}".lower()
            
            if any(kw in full_text for kw in keywords):
                trend = t["trend_neutral"]
                trend_color = "#6c757d"
                if any(word in full_text for word in ["tăng", "lập đỉnh", "vọt", "bật tăng", "vượt", "rise", "jump"]):
                    trend = t["trend_up"]
                    trend_color = "#28a745"
                elif any(word in full_text for word in ["giảm", "lao dốc", "tụt", "rớt", "bốc hơi", "drop", "fall"]):
                    trend = t["trend_down"]
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

def filter_specialized_news(articles, keywords):
    filtered = []
    for item in articles:
        full_text = f"{item['title']} {item['summary']}".lower()
        if any(kw.lower() in full_text for kw in keywords):
            filtered.append(item)
    return filtered

# ==============================================================================
# GIAO DIỆN STREAMLIT
# ==============================================================================
st.set_page_config(page_title="Visual Daily News & Industry Dashboard", layout="wide")

# Thanh chọn Ngôn ngữ (Sidebar)
lang_choice = st.sidebar.radio("🌐 Language / Ngôn ngữ", ["Tiếng Việt", "English"])
lang = "VI" if lang_choice == "Tiếng Việt" else "EN"
t = LANG_TEXT[lang]

# CSS Customing
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

st.title(t["title"])
st.caption(f"🚀 **{t['author']}**")

if st.button(t["btn_refresh"]):
    st.cache_data.clear()

@st.cache_data(ttl=900)
def load_data_by_lang(lang_code):
    feeds = RSS_FEEDS_CONFIG[lang_code]
    vn_raw = get_all_news(feeds["Trong nước"])
    world_raw = get_all_news(feeds["Thế giới"])
    tech_raw = get_all_news(feeds["Công nghệ & Năng lượng"])
    market_raw = get_all_news(feeds["Thị trường & Trung Quốc"])
    gold_data = fetch_gold_trends(lang_code)
    return vn_raw, world_raw, tech_raw, market_raw, gold_data

with st.spinner(t["spinner"]):
    vn_news, world_news, tech_news, market_news, gold_news = load_data_by_lang(lang)

# Keyword filters theo ngôn ngữ
energy_keywords = ["năng lượng", "bess", "pin", "nguồn điện", "điện gió", "mặt trời", "renewable", "battery", "grid", "power", "energy storage"]
china_keywords = ["trung quốc", "china", "xuất khẩu", "kinh doanh", "mặt hàng", "sản xuất", "export", "manufacturing", "trade", "market"]

energy_bess_news = filter_specialized_news(tech_news + world_news + vn_news, energy_keywords)
china_biz_news = filter_specialized_news(market_news + world_news, china_keywords)

# ==============================================================================
# PHẦN 1: TỔNG QUAN
# ==============================================================================
st.markdown(f"### {t['sec_overview']}")

trend_counts = {t["trend_up"]: 0, t["trend_down"]: 0, t["trend_neutral"]: 0}
for item in gold_news:
    trend_counts[item["trend"]] += 1

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric(t["metric_vn"], f"{len(vn_news)}")
m2.metric(t["metric_world"], f"{len(world_news)}")
m3.metric(t["metric_energy"], f"{len(energy_bess_news)}")
m4.metric(t["metric_market"], f"{len(china_biz_news)}")
m5.metric(t["metric_gold_trend"], max(trend_counts, key=trend_counts.get) if gold_news else "N/A")

st.markdown("---")

col_chart, col_gold = st.columns([1, 1.8])

with col_chart:
    st.markdown(f"##### {t['chart_title']}")
    if gold_news:
        df_chart = pd.DataFrame(list(trend_counts.items()), columns=['Trend', 'Count'])
        fig = px.pie(
            df_chart, 
            values='Count', 
            names='Trend', 
            hole=0.5,
            color='Trend',
            color_discrete_map={t["trend_up"]: '#28a745', t["trend_down"]: '#dc3545', t["trend_neutral"]: '#6c757d'}
        )
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=220)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(t["chart_no_data"])

with col_gold:
    st.markdown(f"##### {t['gold_articles_title']}")
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
                        <a href="{g_item['link']}" target="_blank">{t['read_original']}</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# ==============================================================================
# PHẦN 2: CHUYÊN MỤC CHUYÊN SÂU
# ==============================================================================
st.markdown(f"### {t['sec_specialized']}")

tab1, tab2 = st.tabs([t["tab_energy"], t["tab_china"]])

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
                        <div class="news-meta">{item['source']} | <a href="{item['link']}" target="_blank">{t['read_original']}</a></div>
                        <div class="bullet-summary">
                            <b>{t['summary_label']}</b><br>
                            {bullet_text.replace('\n', '<br>')}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info(t["no_energy_news"])

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
                        <div class="news-meta">{item['source']} | <a href="{item['link']}" target="_blank">{t['read_original']}</a></div>
                        <div class="bullet-summary">
                            <b>{t['summary_label']}</b><br>
                            {bullet_text.replace('\n', '<br>')}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info(t["no_china_news"])

st.markdown("---")

# ==============================================================================
# PHẦN 3: TIN TỨC CHUNG
# ==============================================================================
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"## {t['sec_vn_news']}")
    for idx, item in enumerate(vn_news[:6]):
        bullet_text = generate_bullet_summary(item['summary'])
        st.markdown(f"""
            <div class="news-card">
                <div class="news-title">{idx+1}. {item['title']}</div>
                <div class="news-meta">{item['source']} | <a href="{item['link']}" target="_blank">{t['read_original']}</a></div>
                <div class="bullet-summary">
                    <b>{t['summary_label']}</b><br>
                    {bullet_text.replace('\n', '<br>')}
                </div>
            </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown(f"## {t['sec_world_news']}")
    for idx, item in enumerate(world_news[:6]):
        bullet_text = generate_bullet_summary(item['summary'])
        st.markdown(f"""
            <div class="news-card-global">
                <div class="news-title">{idx+1}. {item['title']}</div>
                <div class="news-meta">{item['source']} | <a href="{item['link']}" target="_blank">{t['read_original']}</a></div>
                <div class="bullet-summary">
                    <b>{t['summary_label']}</b><br>
                    {bullet_text.replace('\n', '<br>')}
                </div>
            </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# PHẦN 4: NHÀ ĐẤT PHAN RANG - THÁP CHÀM
# ==============================================================================
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus

def fetch_property_candidates(days=90, limit_per_feed=30):
    """Tìm tin ứng viên qua Google News RSS; không thay thế xác minh tin gốc."""
    queries = [
        '"bán nhà" "Phan Rang" "sổ" "ô tô"',
        '"bán nhà" "Phan Rang" "sổ hồng"',
        '"bán nhà" "Tháp Chàm" "ô tô"',
        'site:batdongsan.com.vn bán nhà Phan Rang sổ',
        'site:nhatot.com bán nhà Phan Rang ô tô',
        'site:homedy.com bán nhà Phan Rang'
    ]
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    results = []
    seen_links = set()

    for query in queries:
        rss_url = (
            "https://news.google.com/rss/search?q="
            + quote_plus(query + " when:" + str(days) + "d")
            + "&hl=vi&gl=VN&ceid=VN:vi"
        )
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:limit_per_feed]:
                link = entry.get("link", "")
                if not link or link in seen_links:
                    continue

                published = entry.get("published_parsed")
                if not published:
                    # Không đoán ngày đăng nếu RSS không cung cấp ngày.
                    continue

                published_dt = datetime.fromtimestamp(
                    time.mktime(published), tz=timezone.utc
                )
                if published_dt < cutoff or published_dt > datetime.now(timezone.utc):
                    continue

                title = clean_html(entry.get("title", ""))
                summary = clean_html(entry.get("summary", ""))
                full_text = f"{title} {summary}".lower()

                # Giữ các tin có liên quan đến nhà/nhà riêng tại Phan Rang.
                location_ok = any(x in full_text for x in [
                    "phan rang", "phường đô vinh", "đô vinh",
                    "tháp chàm", "ninh thuận", "ninh thuan"
                ])
                house_ok = any(x in full_text for x in [
                    "bán nhà", "nhà cấp", "nhà riêng", "nhà phố",
                    "nhà ở", "nhà 1 trệt", "nhà một trệt"
                ])
                if not (location_ok and house_ok):
                    continue

                price_vnd = extract_property_price(full_text)
                if price_vnd is not None and price_vnd >= 1_500_000_000:
                    continue

                legal_ok = any(x in full_text for x in [
                    "có sổ", "sổ đỏ", "sổ hồng", "sổ riêng",
                    "sổ chính chủ", "pháp lý đầy đủ", "sổ hoàn công"
                ])
                car_ok = any(x in full_text for x in [
                    "đường ô tô", "đường oto", "ô tô vào nhà", "oto vào nhà",
                    "ô tô tới nhà", "đường xe hơi", "ô tô tránh",
                    "đường 4m", "đường rộng 4m", "đường 5m",
                    "xe hơi vào nhà"
                ])

                # Không coi tin thiếu giá là đã đạt giới hạn giá.
                status = []
                if price_vnd is None:
                    status.append("Chưa xác định được giá")
                if not legal_ok:
                    status.append("Chưa thấy bằng chứng có sổ")
                if not car_ok:
                    status.append("Chưa thấy bằng chứng đường ô tô")
                if not status:
                    status.append("Đạt từ khóa — vẫn cần xác minh thực tế")

                results.append({
                    "Tiêu đề": title,
                    "Giá phát hiện (ước tính)": (
                        f"{price_vnd:,.0f} đ" if price_vnd is not None
                        else "Chưa xác định"
                    ),
                    "Ngày đăng": published_dt.astimezone().strftime("%d/%m/%Y"),
                    "Có từ khóa sổ": "Có" if legal_ok else "Chưa rõ",
                    "Có từ khóa ô tô": "Có" if car_ok else "Chưa rõ",
                    "Trạng thái": " | ".join(status),
                    "Tóm tắt": summary[:350],
                    "Liên kết": link,
                    "_price_vnd": price_vnd,
                    "_legal_ok": legal_ok,
                    "_car_ok": car_ok
                })
                seen_links.add(link)
        except Exception:
            # Một nguồn lỗi không làm dừng toàn bộ dashboard.
            continue

    return results


def extract_property_price(text):
    """Ước lượng giá từ cách viết phổ biến trong tin đăng tiếng Việt."""
    s = (text or "").lower().replace(",", ".")
    # Ví dụ: 1 tỷ 300 triệu; 1.2 tỷ; 950 triệu
    m = re.search(
        r'(\d+(?:\.\d+)?)\s*tỷ\s*(?:(\d+(?:\.\d+)?)\s*triệu)?',
        s
    )
    if m:
        billions = float(m.group(1))
        millions = float(m.group(2) or 0)
        return int(billions * 1_000_000_000 + millions * 1_000_000)

    m = re.search(r'(\d+(?:\.\d+)?)\s*triệu', s)
    if m:
        return int(float(m.group(1)) * 1_000_000)

    # Dạng 1.350.000.000 đ hoặc 1350000000 đồng
    m = re.search(r'(?<!\d)(\d{1,3}(?:\.\d{3}){2,}|\d{9,})(?:\s*(?:đ|đồng|vnd))?', s)
    if m:
        digits = re.sub(r'\D', '', m.group(1))
        value = int(digits)
        if 100_000_000 <= value <= 100_000_000_000:
            return value
    return None


st.markdown("---")
st.markdown("### 🏠 Nhà đất Phan Rang – Tháp Chàm")
st.caption(
    "Bộ lọc tin ứng viên từ Google News RSS. Ngày/giá có thể thiếu hoặc "
    "không chính xác vì đây không phải cơ sở dữ liệu đầy đủ của các sàn."
)

# Liên kết trực tiếp để người dùng tự tìm tin khi RSS không trả kết quả.
st.markdown("#### 🔗 Tìm nhà đất trực tiếp trên các website")
st.markdown(
    "Các liên kết dưới đây mở trang rao bán hoặc tìm kiếm nhà đất Phan Rang. "
    "Bạn vẫn cần kiểm tra từng tin về giá dưới 1,5 tỷ, ngày đăng trong 90 ngày, "
    "sổ pháp lý và đường ô tô."
)
source_cols = st.columns(3)
property_links = [
    ("Batdongsan.com.vn – Nhà đất bán", "https://batdongsan.com.vn/nha-dat-ban-phan-rang-thap-cham-nt"),
    ("Alonhadat – Nhà đất Phan Rang", "https://alonhadat.com.vn/nha-dat/can-ban/nha-dat/ninh-thuan/345/thanh-pho-phan-rang.html"),
    ("Guland – Tìm nhà đất Phan Rang", "https://www.google.com/search?q=" + quote_plus("site:guland.vn mua bán nhà đất Phan Rang Tháp Chàm")),
    ("Nhà Tốt – Tìm nhà Phan Rang", "https://www.google.com/search?q=" + quote_plus("site:nhatot.com bán nhà Phan Rang")),
    ("Muaban.net – Tìm nhà Phan Rang", "https://www.google.com/search?q=" + quote_plus("site:muaban.net/bat-dong-san Phan Rang bán nhà")),
    ("Google – Tin nhà có sổ, đường ô tô", "https://www.google.com/search?q=" + quote_plus('bán nhà Phan Rang dưới 1.5 tỷ sổ hồng đường ô tô')),
    ("Facebook – Bài đăng bán nhà Phan Rang", "https://www.facebook.com/search/posts/?q=" + quote_plus("bán nhà Phan Rang sổ hồng ô tô")),
    ("Google – Bài Facebook được lập chỉ mục", "https://www.google.com/search?q=" + quote_plus('site:facebook.com "bán nhà" "Phan Rang" sổ ô tô')),
]
for i, (label, url) in enumerate(property_links):
    with source_cols[i % 3]:
        st.markdown(f"- [{label}]({url})")
st.markdown("---")

with st.expander("⚙️ Tiêu chí lọc", expanded=True):
    c1, c2, c3 = st.columns(3)
    days_limit = c1.selectbox("Tin đăng trong", [30, 60, 90], index=2,
                              format_func=lambda x: f"{x} ngày gần nhất")
    max_price_billion = c2.number_input(
        "Giá tối đa (tỷ đồng)", min_value=0.1, max_value=20.0,
        value=1.5, step=0.1
    )
    strict_only = c3.checkbox(
        "Chỉ hiện tin có từ khóa sổ + ô tô", value=True
    )

if st.button("🔎 Tìm nhà Phan Rang ngay", key="search_property"):
    with st.spinner("Đang tìm tin nhà đất trên Google News RSS..."):
        st.session_state["property_results"] = fetch_property_candidates(
            days=days_limit
        )
        st.session_state["property_days"] = days_limit
        st.session_state["property_max_price"] = max_price_billion

if "property_results" in st.session_state:
    property_results = st.session_state["property_results"]
    max_price = st.session_state.get("property_max_price", 1.5) * 1_000_000_000

    # Chỉ lọc nghiêm ngặt khi đã tìm thấy giá, từ khóa sổ và từ khóa ô tô.
    if strict_only:
        visible_results = [
            x for x in property_results
            if x["_price_vnd"] is not None
            and x["_price_vnd"] < max_price
            and x["_legal_ok"] and x["_car_ok"]
        ]
    else:
        visible_results = [
            x for x in property_results
            if x["_price_vnd"] is None or x["_price_vnd"] < max_price
        ]

    st.metric("Số tin phù hợp với bộ lọc từ khóa", len(visible_results))
    if visible_results:
        display_df = pd.DataFrame([
            {k: v for k, v in item.items() if not k.startswith("_")}
            for item in visible_results
        ])
        st.dataframe(
            display_df.drop(columns=["Liên kết"], errors="ignore"),
            use_container_width=True,
            hide_index=True
        )
        for item in visible_results:
            st.markdown(
                f"- **[{item['Tiêu đề']}]({item['Liên kết']})** — "
                f"{item['Giá phát hiện (ước tính)']} · {item['Ngày đăng']}  \n"
                f"Pháp lý: {item['Có từ khóa sổ']} · "
                f"Đường ô tô: {item['Có từ khóa ô tô']} · "
                f"{item['Trạng thái']}"
            )
        export_df = pd.DataFrame([
            {k: v for k, v in item.items() if not k.startswith("_")}
            for item in visible_results
        ])
        st.download_button(
            "⬇️ Tải danh sách nhà ra CSV",
            data=export_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="nha_phan_rang.csv",
            mime="text/csv"
        )
    else:
        st.warning(
            "Chưa tìm thấy tin nào đủ các điều kiện trong dữ liệu RSS hiện tại. "
            "Hãy bỏ chọn bộ lọc nghiêm ngặt để xem các tin cần xác minh, "
            "hoặc kiểm tra trực tiếp các website rao bán."
        )

st.info(
    "Lưu ý: kết quả RSS chỉ giúp sàng lọc ban đầu. Cần mở tin gốc để xác minh "
    "ngày đăng, giá bán, sổ đỏ/sổ hồng, quy hoạch và đường ô tô thực tế. "
    "Một tin không xuất hiện ở đây không có nghĩa là không tồn tại."
)


# ==============================================================================
# CHÂN TRANG
# ==============================================================================
st.markdown(f"""
    <div class="footer">
        © Daily News & Financial Dashboard | <strong>{t['author']}</strong>
    </div>
""", unsafe_allow_html=True)
