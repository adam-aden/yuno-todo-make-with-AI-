import streamlit as st
import requests
import time
import os

st.set_page_config(
    page_title="Yuno Floating VN",
    page_icon="💜",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS จัดส่วนหัวให้อยู่ติดจอ (Sticky) เสมือนกล่องลอยตัวแบบในตัวอย่าง
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0b10;
        color: #ffffff;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* กล่องควบคุมด้านบนสุดให้ตรึงติดจอเวลาเลื่อนหน้าจอ */
    .sticky-header {
        position: sticky;
        top: 0px;
        z-index: 999;
        background-color: #0b0b10;
        padding-top: 10px;
        padding-bottom: 10px;
        border-bottom: 1px solid #2b2b36;
    }
    </style>
""", unsafe_allow_html=True)

if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'dialogue' not in st.session_state:
    st.session_state.dialogue = "สวัสดีค่ะ! วันนี้มีอะไรให้ฉันช่วยบันทึกบ้างคะ?"
if 'current_img' not in st.session_state:
    st.session_state.current_img = "static/idle.png"
if 'menu_mode' not in st.session_state:
    st.session_state.menu_mode = "💬 พูดคุย"
if 'box_opacity' not in st.session_state:
    st.session_state.box_opacity = 0.90

def fetch_earthquake_data():
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=1"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            features = data.get('features', [])
            if features:
                place = features[0]['properties']['place']
                mag = features[0]['properties']['mag']
                return f"⚠️ รายงานแผ่นดินไหวล่าสุด: ขนาด {mag} Mv ที่ {place}"
            return "ไม่พบรายงานแผ่นดินไหวล่าสุดในตอนนี้ค่ะ"
        return "ไม่สามารถเชื่อมต่อระบบรายงานภัยธรรมชาติได้"
    except:
        return "เกิดข้อผิดพลาดในการเชื่อมต่อเครือข่าย"

# -------------------------------------------------------------
# ส่วนหัวแบบลอยติดจอ (Sticky Header): ตัวละคร (ซ้าย) + กล่องข้อความ (ขวา) + เมนู
# -------------------------------------------------------------
st.markdown('<div class="sticky-header">', unsafe_allow_html=True)

# แถบเมนูซ้ายขวาแบบกระชับ
col_l, col_m, col_r = st.columns([1, 2, 1])
modes = ["💬 พูดคุย", "📋 To-Do List", "🌐 แผ่นดินไหว"]
current_idx = modes.index(st.session_state.menu_mode)

with col_l:
    if st.button("◀️ ก่อน", use_container_width=True):
        new_idx = (current_idx - 1) % len(modes)
        st.session_state.menu_mode = modes[new_idx]
        if st.session_state.menu_mode == "🌐 แผ่นดินไหว":
            st.session_state.dialogue = fetch_earthquake_data()
            st.session_state.current_img = "static/alert.png"
        else:
            st.session_state.current_img = "static/idle.png"
            st.session_state.dialogue = "เปลี่ยนโหมดแล้ว มีอะไรให้ช่วยไหม?"
        st.rerun()

with col_m:
    st.markdown(f"<p style='text-align: center; margin: 2px; font-weight: bold; color: #a29bfe; font-size: 13px;'>📌 {st.session_state.menu_mode}</p>", unsafe_allow_html=True)

with col_r:
    if st.button("ถัดไป ▶️", use_container_width=True):
        new_idx = (current_idx + 1) % len(modes)
        st.session_state.menu_mode = modes[new_idx]
        if st.session_state.menu_mode == "🌐 แผ่นดินไหว":
            st.session_state.dialogue = fetch_earthquake_data()
            st.session_state.current_img = "static/alert.png"
        else:
            st.session_state.current_img = "static/idle.png"
            st.session_state.dialogue = "เปลี่ยนโหมดแล้ว มีอะไรให้ช่วยไหม?"
        st.rerun()

# จัดวางตัวละคร (ซ้าย) และกล่องข้อความ (ขวา) แบบสไตล์ตัวอย่าง
col_char, col_bubble = st.columns([1, 2], vertical_alignment="center")

with col_char:
    if os.path.exists(st.session_state.current_img):
        st.image(st.session_state.current_img, use_container_width=True)
    else:
        st.warning("⚠️ ไม่พบรูป")

with col_bubble:
    opacity_val = st.slider("🎚️ ปรับความเข้มกล่อง", 0.3, 1.0, st.session_state.box_opacity, 0.1, label_visibility="collapsed")
    st.session_state.box_opacity = opacity_val
    bg_color = f"rgba(25, 25, 35, {opacity_val})"
    
    st.markdown(f"""
        <div style="
            background-color: {bg_color};
            border: 2px solid #a29bfe;
            border-radius: 12px;
            padding: 10px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.7);
            min-height: 75px;
        ">
            <span style="font-size: 11px; color: #d6a2e8; font-weight: bold;">Yuno:</span>
            <p style="font-size: 13px; margin-top: 2px; color: #ffffff; margin-bottom: 0px;">{st.session_state.dialogue}</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # ปิด Sticky Header

st.divider()

# -------------------------------------------------------------
# เนื้อหาด้านล่าง (สามารถเลื่อนฟีดดู To-Do List ได้อิสระ โดยที่ตัวละครด้านบนจะลอยตามติดจอ)
# -------------------------------------------------------------
if st.session_state.menu_mode == "💬 พูดคุย":
    st.info("💡 ทริป: ตัวละครและกล่องข้อความด้านบนจะลอยติดจออยู่เสมอ เวลาคุณเพิ่ม To-Do List ด้านล่าง สามารถเลื่อนหน้าจอได้ตามสบายเลยค่ะ!")

elif st.session_state.menu_mode == "📋 To-Do List":
    # ช่องพิมพ์พร้อมปุ่ม ^ ด้านข้าง
    with st.form(key="vn_todo_form", clear_on_submit=True):
        col_input, col_btn = st.columns([4, 1])
        with col_input:
            new_task = st.text_input("เพิ่มสิ่งที่ต้องทำ:", placeholder="พิมพ์งานที่นี่...", label_visibility="collapsed")
        with col_btn:
            submit_t = st.form_submit_button(" ^ ", use_container_width=True)
            
        if submit_t and new_task.strip():
            st.session_state.tasks.append({"title": new_task.strip(), "done": False})
            st.session_state.dialogue = f"เพิ่มรายการ '{new_task.strip()}' เรียบร้อยแล้ว!"
            st.session_state.current_img = "static/idle.png"
            st.rerun()

    # รายการ To-Do (กดเช็คแล้วเปลี่ยนเป็นภาพชูนิ้วยิ้มค้างไว้ 3 วินาที)
    if st.session_state.tasks:
        st.markdown("---")
        for idx, task in enumerate(st.session_state.tasks):
            c_chk, c_del = st.columns([5, 1])
            is_done = c_chk.checkbox(task["title"], value=task["done"], key=f"vn_chk_{idx}")
            
            if is_done != task["done"]:
                st.session_state.tasks[idx]["done"] = is_done
                if is_done:
                    st.session_state.dialogue = "เก่งมากเลยค่ะ! ทำสำเร็จไปอีกหนึ่งอย่างแล้วนะ 👍✨"
                    st.session_state.current_img = "static/praise.png"
                    st.rerun()
                else:
                    st.session_state.dialogue = "อ้าว ยกเลิกสถานะทำเสร็จซะแล้ว สู้ๆ นะคะ!"
                    st.session_state.current_img = "static/idle.png"
                    st.rerun()
                    
            if c_del.button("🗑️", key=f"vn_del_{idx}"):
                st.session_state.tasks.pop(idx)
                st.session_state.dialogue = "ลบรายการออกให้เรียบร้อยแล้วค่ะ"
                st.rerun()
    else:
        st.caption("📌 ยังไม่มีรายการ To-Do List พิมพ์เพิ่มด้านบนแล้วกดปุ่ม ^ ได้เลยค่ะ")

elif st.session_state.menu_mode == "🌐 แผ่นดินไหว":
    if st.button("🔄 อัปเดตข้อมูลแผ่นดินไหวล่าสุด", use_container_width=True):
        st.session_state.dialogue = fetch_earthquake_data()
        st.session_state.current_img = "static/alert.png"
        st.rerun()

# -------------------------------------------------------------
# ระบบหน่วงเวลา 3 วินาที เมื่อกดติ๊กถูก To-Do สำเร็จ
# -------------------------------------------------------------
if st.session_state.current_img == "static/praise.png":
    time.sleep(3)
    st.session_state.current_img = "static/idle.png"
    st.session_state.dialogue = "스ู้ๆ กับงานที่เหลือต่อนะ ฉันคอยเอาใจช่วยอยู่!"
    st.rerun()
