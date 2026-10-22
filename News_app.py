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
