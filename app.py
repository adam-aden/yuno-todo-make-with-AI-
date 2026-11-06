import streamlit as st
import requests
import time
import os

# ตั้งค่าหน้าเว็บ (Mobile-Friendly)
st.set_page_config(
    page_title="Yuno To-Do Companion",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS จัดแต่งหน้าจอให้เหมือนแอปมือถือ
st.markdown("""
    <style>
    .stApp {
        background-color: #1a1a24;
        color: #ffffff;
    }
    .chat-bubble {
        background-color: #2b2b36;
        border-radius: 15px;
        padding: 12px;
        margin-left: 5px;
        border: 2px solid #6c5ce7;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
        font-size: 14px;
        min-height: 70px;
        display: flex;
        align-items: center;
    }
    .character-img img {
        max-width: 100% !important;
        height: auto;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# จัดการ State (ความจำของแอปชั่วคราว)
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

if 'dialogue' not in st.session_state:
    st.session_state.dialogue = "สวัสดี! วันนี้มีอะไรให้ฉันช่วยจดบ้างล่ะ?"

if 'current_img' not in st.session_state:
    st.session_state.current_img = "static/idle.png"

# ฟังก์ชันดึงข้อมูลแผ่นดินไหว / ภัยธรรมชาติจาก USGS API
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
        return "เชื่อมต่อระบบรายงานภัยธรรมชาติไม่ได้"
    except Exception as e:
        return f"เกิดข้อผิดพลาด: ระบบเน็ตอาจมีปัญหา"

# ----------------
# ส่วนบน: ตัวละคร (ซ้าย) + กล่องคำพูด (ขวา)
# ----------------
col_img, col_text = st.columns([1, 2], vertical_alignment="center")

with col_img:
    st.markdown('<div class="character-img">', unsafe_allow_html=True)
    if os.path.exists(st.session_state.current_img):
        st.image(st.session_state.current_img, use_container_width=True)
    else:
        # กรณีหาไฟล์รูปไม่เจอ ให้แสดงข้อความสำรอง
        st.info("📷 รอโหลดรูปตัวละคร")
    st.markdown('</div>', unsafe_allow_html=True)

with col_text:
    st.markdown(f'<div class="chat-bubble">{st.session_state.dialogue}</div>', unsafe_allow_html=True)

st.divider()

# ปุ่มเช็คแผ่นดินไหว
if st.button("🌐 เช็ครายงานแผ่นดินไหว / ภัยพิบัติ", use_container_width=True):
    earthquake_msg = fetch_earthquake_data()
    st.session_state.dialogue = earthquake_msg
    st.session_state.current_img = "static/alert.png"
    st.rerun()

st.subheader("📋 To-Do List ของคุณ")

# ฟอร์มเพิ่มรายการ
with st.form(key="add_task_form", clear_on_submit=True):
    new_task = st.text_input("พิมพ์หัวข้อสิ่งที่ต้องทำ:", placeholder="เช่น ทำการบ้านวิชา...")
    submit_button = st.form_submit_button(label="➕ เพิ่มรายการ", use_container_width=True)
    
    if submit_button and new_task.strip():
        st.session_state.tasks.append({"title": new_task.strip(), "done": False})
        st.session_state.dialogue = f"บันทึก '{new_task.strip()}' เรียบร้อย! ลุยกันเลย"
        st.session_state.current_img = "static/idle.png"
        st.rerun()

# แสดงรายการ To-Do
if not st.session_state.tasks:
    st.caption("ยังไม่มีรายการในตอนนี้ พิมพ์เพิ่มด้านบนได้เลย!")
else:
    for idx, task in enumerate(st.session_state.tasks):
        c1, c2 = st.columns([4, 1])
        
        is_done = c1.checkbox(task["title"], value=task["done"], key=f"check_{idx}")
        
        if is_done != task["done"]:
            st.session_state.tasks[idx]["done"] = is_done
            if is_done:
                st.session_state.dialogue = "เก่งมาก! ทำสำเร็จไปอีกหนึ่งอย่างแล้วนะ ^_^"
                st.session_state.current_img = "static/praise.png"
                st.rerun()
            else:
                st.session_state.dialogue = "อ่าว ยกเลิกเช็คซะงั้น สู้ๆ นะ!"
                st.session_state.current_img = "static/idle.png"
                st.rerun()

        if c2.button("🗑️", key=f"del_{idx}"):
            removed_item = st.session_state.tasks.pop(idx)
            st.session_state.dialogue = f"ลบ '{removed_item['title']}' ออกจากลิสต์แล้ว"
            st.session_state.current_img = "static/idle.png"
            st.rerun()

# ระบบหน่วงเวลา 2 วินาที เมื่อกดเช็คสำเร็จ (เปลี่ยนภาพกลับเป็นปกติ)
if st.session_state.current_img == "static/praise.png":
    time.sleep(2)
    st.session_state.current_img = "static/idle.png"
    st.session_state.dialogue = "สู้ๆ กับงานที่เหลือต่อนะ!"
    st.rerun()
