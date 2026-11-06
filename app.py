import streamlit as st
import requests
import time
import os

st.set_page_config(
    page_title="Yuno VN Companion",
    page_icon="💜",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ปรับ CSS ให้กล่องข้อความทับซ้อนอยู่ด้านล่างของตัวละคร และจัดหน้าจอให้พอดีมือถือ
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0b10;
        color: #ffffff;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* กรอบ VN หลัก */
    .vn-screen {
        position: relative;
        width: 100%;
        max-width: 450px;
        margin: 0 auto;
        text-align: center;
    }
    .vn-character {
        width: 100%;
        max-height: 420px;
        object-fit: contain;
    }
    </style>
""", unsafe_allow_html=True)

if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'dialogue' not in st.session_state:
    st.session_state.dialogue = "ยินดีต้อนรับค่ะ วันนี้มีอะไรให้ฉันช่วยดูแลหรือเปล่า?"
if 'current_img' not in st.session_state:
    st.session_state.current_img = "static/idle.png"
if 'menu_mode' not in st.session_state:
    st.session_state.menu_mode = "💬 พูดคุย"
if 'box_opacity' not in st.session_state:
    st.session_state.box_opacity = 0.85

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
# เมนูเลือกโหมด (ไว้ด้านบนสุดเพื่อให้กดง่าย ไม่ต้องเลื่อนจอ)
# -------------------------------------------------------------
col_l, col_m, col_r = st.columns([1, 2, 1])
modes = ["💬 พูดคุย", "📋 To-Do List", "🌐 แผ่นดินไหว"]
current_idx = modes.index(st.session_state.menu_mode)

with col_l:
    if st.button("◀️ ก่อนหน้า", use_container_width=True):
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
    st.markdown(f"<p style='text-align: center; margin: 5px; font-weight: bold; color: #a29bfe; font-size: 14px;'>📌 {st.session_state.menu_mode}</p>", unsafe_allow_html=True)

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

# -------------------------------------------------------------
# ส่วนแสดงตัวละคร VN
# -------------------------------------------------------------
st.markdown('<div class="vn-screen">', unsafe_allow_html=True)
if os.path.exists(st.session_state.current_img):
    st.image(st.session_state.current_img, use_container_width=True)
else:
    st.warning("⚠️ ไม่พบไฟล์รูปภาพในโฟลเดอร์ static/")
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# กล่องข้อความสไตล์ VN (ซ้อนทับบังขาเล็กน้อยตามแบบ VN) + ตัวปรับความเข้มจาง
# -------------------------------------------------------------
opacity_val = st.slider("🎚️ ปรับความเข้มจางกล่องข้อความ", 0.3, 1.0, st.session_state.box_opacity, 0.05, label_visibility="collapsed")
st.session_state.box_opacity = opacity_val
bg_color = f"rgba(20, 20, 30, {opacity_val})"

st.markdown(f"""
    <div style="
        background-color: {bg_color};
        border: 2px solid #a29bfe;
        border-radius: 12px;
        padding: 12px;
        margin-top: -30px;
        margin-bottom: 10px;
        box-shadow: 0px -4px 15px rgba(0,0,0,0.8);
        min-height: 80px;
        position: relative;
        z-index: 10;
    ">
        <span style="font-size: 12px; color: #d6a2e8; font-weight: bold;">Yuno:</span>
        <p style="font-size: 15px; margin-top: 3px; color: #ffffff; margin-bottom: 0px;">{st.session_state.dialogue}</p>
    </div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# เนื้อหาภายในโหมดต่างๆ (To-Do List / แผ่นดินไหว)
# -------------------------------------------------------------
if st.session_state.menu_mode == "💬 พูดคุย":
    st.caption("💡 ทริป: ใช้ปุ่มซ้าย-ขวาด้านบน เพื่อเปิด To-Do List หรือเช็คแผ่นดินไหว")

elif st.session_state.menu_mode == "📋 To-Do List":
    # ฟอร์มเพิ่ม To-Do พร้อมปุ่ม ^
    with st.form(key="vn_todo_form", clear_on_submit=True):
        col_input, col_btn = st.columns([4, 1])
        with col_input:
            new_task = st.text_input("เพิ่มสิ่งที่ต้องทำ:", placeholder="พิมพ์งานที่นี่...", label_visibility="collapsed")
        with col_btn:
            submit_t = st.form_submit_button(" ^ ", use_container_width=True)
            
        if submit_t and new_task.strip():
            st.session_state.tasks.append({"title": new_task.strip(), "done": False})
            st.session_state.dialogue = f"จดรายการ '{new_task.strip()}' ให้เรียบร้อยแล้วค่ะ!"
            st.session_state.current_img = "static/idle.png"
            st.rerun()

    # รายการ To-Do (กดเช็คแล้วเปลี่ยนเป็นภาพชูนิ้วยิ้ม 3 วินาที)
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
    st.session_state.dialogue = "สู้ๆ กับงานที่เหลือต่อนะ ฉันคอยเอาใจช่วยอยู่!"
    st.rerun()
