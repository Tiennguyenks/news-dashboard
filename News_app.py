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
