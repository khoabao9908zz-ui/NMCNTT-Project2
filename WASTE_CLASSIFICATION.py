import base64
import hashlib
import io
import os
from datetime import datetime

import pandas as pd
import requests
from PIL import Image
import streamlit as st

# ----------------------------------------------------------------------------
# 1. CẤU HÌNH TRANG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="EcoSort AI - Đồ án CSC00004",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# 2. DỮ LIỆU CẤU HÌNH NHÃN RÁC & CẨM NANG XỬ LÝ XANH
# ----------------------------------------------------------------------------
CLASSES_MAP = {
    "cardboard": {
        "vi": "Bìa các-tông",
        "bin": "Tái chế",
        "color": "#0284C7",
        "tip": "Hành động xanh: Tháo gỡ băng keo, gỡ bỏ ghim bấm và gấp phẳng thùng carton. Giúp tiết kiệm không gian và đẩy nhanh quá trình tái chế bột giấy.",
    },
    "paper": {
        "vi": "Giấy",
        "bin": "Tái chế",
        "color": "#0284C7",
        "tip": "Hành động xanh: Phân loại riêng giấy sạch, khô ráo (sách vở cũ, báo, giấy A4). Lưu ý: Tuyệt đối không bỏ giấy dính dầu mỡ (hộp pizza) vào đây để tránh làm hỏng mẻ tái chế.",
    },
    "plastic": {
        "vi": "Nhựa (Chai, lọ, túi)",
        "bin": "Tái chế",
        "color": "#0284C7",
        "tip": "Hành động xanh: Súc rửa sạch, đổ hết chất lỏng thừa, bóp dẹp vỏ chai/hộp nhựa và đậy nắp lại. Giúp giảm thể tích rác và ngăn mùi hôi tại trạm tập kết.",
    },
    "glass": {
        "vi": "Thủy tinh",
        "bin": "Tái chế",
        "color": "#0284C7",
        "tip": "Hành động xanh: Làm sạch chai lọ, tháo rời nắp nhựa/kim loại. An toàn: Nếu thủy tinh bị vỡ, hãy dùng giấy báo bọc kín nhiều lớp trước khi bỏ vào thùng để bảo vệ cô chú công nhân vệ sinh.",
    },
    "metal": {
        "vi": "Kim loại (Lon, hộp)",
        "bin": "Tái chế",
        "color": "#0284C7",
        "tip": "Hành động xanh: Tráng sạch lon nước ngọt hoặc hộp thực phẩm bằng một ít nước, ép dẹp nếu có thể. Kim loại tái chế 100% không bị giảm chất lượng!",
    },
    "trash": {
        "vi": "Rác thải khác / Khác",
        "bin": "Rác còn lại",
        "color": "#64748B",
        "tip": "Hành động xanh: Gom các vật liệu không thể tái chế (màng bọc bẩn, xốp, nhựa pha tạp) vào một túi riêng. Buộc kín miệng túi thật chặt trước khi bỏ vào thùng rác sinh hoạt.",
    },
}

# ----------------------------------------------------------------------------
# 3. GIAO DIỆN (CSS TƯƠI MÁT, HIỆN ĐẠI)
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"], .stMarkdown, button, input, textarea {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .block-container { padding-top: 2rem; max-width: 1200px; }
    .stApp { background-color: #F8FAF9; }

    .hero {
        background: linear-gradient(135deg, #0F766E 0%, #14B8A6 100%); 
        color: #FFFFFF; border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(20, 184, 166, 0.2);
    }
    .hero h1 { color: #FFFFFF; font-weight: 800; font-size: 2.2rem; margin: 0 0 .4rem 0; }
    .hero p  { color: #E6FFFA; margin: 0; font-size: 1.1rem; }

    .result-card {
        border-radius: 14px; padding: 1.5rem; margin-bottom: 1rem;
        background: #FFFFFF; border: 1px solid #E2E8F0; border-left-width: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .result-card .label { font-size: 1.8rem; font-weight: 800; color: #0F172A; line-height: 1.2; }
    .result-card .bin   { font-size: 1rem; font-weight: 700; margin-top: .4rem; text-transform: uppercase; }
    .result-card .tip   { color: #334155; margin-top: .8rem; font-size: 0.95rem; background: #F8FAFC; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #14B8A6; line-height: 1.5; }

    div[data-testid="stMetric"] {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1rem 1.2rem;
    }
    div[data-testid="stMetric"] label { color: #64748B !important; font-weight: 600 !important; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #0F766E !important; font-weight: 800 !important; }
    section[data-testid="stSidebar"] { background-color: #F0FDF4; border-right: 1px solid #DCFCE7; }
    .footer { text-align: center; color: #64748B; font-size: 0.9rem; margin-top: 3rem; padding: 1rem 0; border-top: 1px solid #E2E8F0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# 4. SESSION STATE & KẾT NỐI OPENAI-COMPATIBLE API
# ----------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.vilao.ai/v1").strip().rstrip("/")
OPENAI_MODEL = os.environ.get("VILAO_MODEL", "gemini-3.8-flash").strip()
MAX_IMAGE_SIZE_BYTES = 50 * 1024 * 1024


def openai_api_error(response: requests.Response) -> str:
    try:
        response_data = response.json()
    except ValueError:
        return "Không có chi tiết lỗi."

    error_data = response_data.get("error", {}) if isinstance(response_data, dict) else {}
    if isinstance(error_data, dict):
        return str(error_data.get("message", "Không có chi tiết lỗi."))
    return "Không có chi tiết lỗi."


def classify_via_openai(image_bytes: bytes, mime_type: str, source: str) -> dict:
    api_key = os.environ.get("VILAO_API_KEY", "").strip() or os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Chưa cấu hình VILAO_API_KEY. Hãy đặt API key trong terminal rồi khởi động lại ứng dụng."
        )
    if not OPENAI_MODEL:
        raise RuntimeError(
            "Chưa cấu hình VILAO_MODEL. Hãy đặt model ID được hỗ trợ trong dashboard Vilao."
        )
    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise RuntimeError("Ảnh vượt quá giới hạn 50MB.")

    prompt = (
        "Bạn là chuyên gia phân loại rác thải. Hãy nhận diện tất cả các loại rác "
        "thực sự nhìn thấy trong ảnh, không tự suy đoán vật thể bị che khuất. "
        "Trả lời bằng tiếng Việt, dạng văn bản thuần; không dùng JSON, markdown, "
        "ký tự **, dấu # hoặc khối code. Liệt kê riêng từng loại rác theo đúng "
        "mẫu sau, đánh số liên tục:\n\n"
        "1. <Tên rác>\n"
        "Loại rác: <phân loại vật liệu>\n"
        "Nguồn gốc: <nguồn gốc hoặc mục đích sử dụng thường gặp>\n"
        "Khả năng phân hủy: <mô tả>\n"
        "Cách xử lý tái chế: <hướng dẫn>\n\n"
        "Nếu ảnh không có rác thải, chỉ trả lời: Không phát hiện rác thải."
    )
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"
                        },
                    },
                ],
            }
        ],
    }

    try:
        response = requests.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=(10, 180),
        )
    except requests.RequestException as error:
        raise RuntimeError("Không thể kết nối tới Vilao API.") from error

    try:
        response_data = response.json()
    except ValueError as error:
        raise RuntimeError("Vilao API trả về dữ liệu không hợp lệ.") from error

    if not isinstance(response_data, dict):
        raise RuntimeError("Vilao API trả về dữ liệu không đúng định dạng.")
    if not response.ok:
        raise RuntimeError(
            f"Vilao API trả về lỗi ({response.status_code}): "
            f"{openai_api_error(response)}"
        )

    try:
        content = response_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError("Phản hồi từ Vilao API không đúng định dạng.") from error
    if isinstance(content, list):
        content = "".join(
            part["text"]
            for part in content
            if isinstance(part, dict) and isinstance(part.get("text"), str)
        )
    if not content:
        raise RuntimeError("Vilao API không trả về nội dung văn bản.")
    if not isinstance(content, str):
        raise RuntimeError("Vilao API trả về nội dung không phải văn bản.")

    answer_lines = content.strip().splitlines()
    if answer_lines and answer_lines[0].strip().startswith("```"):
        answer_lines = answer_lines[1:]
    if answer_lines and answer_lines[-1].strip() == "```":
        answer_lines = answer_lines[:-1]
    answer = "\n".join(answer_lines).strip()
    if not answer:
        raise RuntimeError("Vilao API không trả về nội dung phân loại.")

    return {
        "time": datetime.now().strftime("%H:%M:%S"),
        "source": source,
        "model": OPENAI_MODEL,
        "answer": answer,
    }


def render_result(res: dict) -> None:
    st.text(res["answer"])
    c1, c2 = st.columns(2)
    c1.metric("Mô hình", res["model"])
    c2.metric("Nguồn hình ảnh", res["source"])

# ----------------------------------------------------------------------------
# 5. SIDEBAR & GIAO DIỆN CHÍNH
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🌿 EcoSort Cloud AI")
    st.caption(f"Engine: Vilao API · {OPENAI_MODEL or 'chưa chọn model'}")
    if os.environ.get("VILAO_API_KEY", "").strip() or os.environ.get("OPENAI_API_KEY", "").strip():
        st.success("Vilao API key đã được cấu hình.")
    else:
        st.warning("Chưa cấu hình VILAO_API_KEY.")
    st.divider()
    st.metric("Tổng ảnh đã phân tích", len(st.session_state.history))
    if st.button("🗑️ Xóa lịch sử", use_container_width=True, disabled=not st.session_state.history):
        st.session_state.history = []
        st.rerun()
    st.divider()
    st.markdown("<div style='text-align: center; color: #0F766E; font-weight: 600;'>Team 03 · CSC00004</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
        <h1>🌿 EcoSort AI - Nhận diện rác thông minh</h1>
        <p>Phân tích hình ảnh qua Vilao API theo chuẩn OpenAI và gợi ý cách xử lý rác phù hợp.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_cam, tab_stats, tab_guide = st.tabs(["📸 Camera Trực Tiếp", "📊 Lịch sử", "📘 Cẩm nang xanh"])

with tab_cam:
    col_cam, col_res = st.columns([1, 1], gap="large")
    image = None
    source = ""
    image_key = ""
    image_bytes = b""
    image_mime_type = ""
    image_file_name = "camera-capture.jpg"
    image_error = ""

    with col_cam:
        input_method = st.radio(
            "Chọn cách đưa ảnh vào",
            ["Tải ảnh lên", "Chụp bằng camera"],
            horizontal=True,
        )

        if input_method == "Tải ảnh lên":
            uploaded_file = st.file_uploader(
                "Chọn ảnh rác từ thiết bị",
                type=["jpg", "jpeg", "png", "webp"],
                help="Hỗ trợ JPG, PNG hoặc WebP, tối đa 50MB.",
                max_upload_size=50,
            )
            if uploaded_file is not None:
                image_bytes = uploaded_file.getvalue()
                image_file_name = uploaded_file.name
                try:
                    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
                        raise ValueError("Ảnh vượt quá giới hạn 50MB.")
                    opened_image = Image.open(io.BytesIO(image_bytes))
                    image_format = opened_image.format
                    image_mime_type = {
                        "JPEG": "image/jpeg",
                        "PNG": "image/png",
                        "WEBP": "image/webp",
                    }.get(image_format or "", "")
                    if not image_mime_type:
                        raise ValueError("Định dạng ảnh không được hỗ trợ.")
                    image = opened_image.convert("RGB")
                    source = f"Tải ảnh lên · {uploaded_file.name}"
                    st.image(image, caption=uploaded_file.name, width="stretch")
                except (OSError, ValueError) as error:
                    image_error = str(error) or "Không thể đọc ảnh này."
                    image = None
        else:
            st.markdown("#### 🔴 Khung ngắm Camera")
            camera_photo = st.camera_input("Đưa rác vào khung hình và bấm nút Chụp ảnh")
            if camera_photo is not None:
                image_bytes = camera_photo.getvalue()
                try:
                    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
                        raise ValueError("Ảnh từ camera vượt quá giới hạn 50MB.")
                    opened_image = Image.open(io.BytesIO(image_bytes))
                    image_format = opened_image.format
                    image_mime_type = {
                        "JPEG": "image/jpeg",
                        "PNG": "image/png",
                        "WEBP": "image/webp",
                    }.get(image_format or "", "")
                    if not image_mime_type:
                        raise ValueError("Định dạng ảnh từ camera không được hỗ trợ.")
                    image = opened_image.convert("RGB")
                    source = "Camera trực tiếp"
                except (OSError, ValueError) as error:
                    image_error = str(error) or "Không thể đọc ảnh từ camera."
                    image = None

        if image is not None:
            image_key = hashlib.sha256(image_bytes).hexdigest()
        elif image_error:
            st.error(image_error)

    with col_res:
        st.markdown("#### 🎯 Kết quả phân tích AI")
        if image is not None:
            if st.button("🔍 Phân tích ảnh", type="primary", width="stretch"):
                with st.spinner(f"⚡ {OPENAI_MODEL or 'AI'} đang phân tích ảnh..."):
                    try:
                        result = classify_via_openai(
                            image_bytes,
                            image_mime_type,
                            source,
                        )
                    except RuntimeError as error:
                        st.error(str(error))
                    else:
                        st.session_state.history.append(result)
                        st.session_state.last_analysis_key = image_key
                        st.session_state.last_analysis = result

            if st.session_state.get("last_analysis_key") == image_key:
                render_result(st.session_state.last_analysis)
            else:
                st.info("Ảnh đã sẵn sàng. Bấm **Phân tích ảnh** để nhận diện.")
        else:
            if input_method == "Tải ảnh lên":
                st.info("💡 Tải ảnh lên để xem trước, sau đó bấm **Phân tích ảnh**.")
            else:
                st.info("💡 Bật camera thiết bị, hướng vào vật thể rác và bấm **Take Photo**.")

with tab_stats:
    hist = st.session_state.history
    if not hist:
        st.info("Chưa có lịch sử phân tích nào.")
    else:
        df = pd.DataFrame(hist)
        history_columns = ["time", "answer", "source", "model"]
        for column in history_columns:
            if column not in df:
                df[column] = "—"
        st.dataframe(df[history_columns], width="stretch")

with tab_guide:
    st.markdown("### 📘 Cẩm nang phân loại và xử lý rác thải")
    st.write("Hệ thống phân loại rác thông minh của EcoSort AI không chỉ giúp bạn nhận biết loại rác mà còn đồng hành cùng lối sống xanh:")
    for _, val in CLASSES_MAP.items():
        st.markdown(f"**🏷️ {val['vi']}** (Thuộc thùng: `{val['bin']}`)")
        st.markdown(f"> {val['tip']}")
        st.divider()

st.markdown('<div class="footer">EcoSort AI · Đồ án Môn học CSC00004 · University of Science</div>', unsafe_allow_html=True)
