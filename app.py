import streamlit as st
from streamlit_calendar import calendar
import datetime
import json
import os

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="🇯🇵 일본사는사람들 일정", layout="wide")

# --- 2. 데이터 저장/로드 ---
DB_FILE = "events.json"
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return []
def save_data(events):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(events, f, ensure_ascii=False, indent=4)

if "events" not in st.session_state:
    st.session_state.events = load_data()

# 💡 [핵심] 상태 관리를 위한 세션 변수들
if "reset_count" not in st.session_state:
    st.session_state.reset_count = 0
if "last_processed_click" not in st.session_state:
    st.session_state.last_processed_click = None

ADMIN_PASSWORD = "admin144" 
current_year = datetime.date.today().year

# --- 3. 🔍 다크모드 대응 고대비 팝업창 ---
@st.dialog("🔍 일정 상세 정보")
def open_popup(ev):
    st.markdown(f"""
    <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; color: #1e1e1e; border: 1px solid #ddd;">
        <h2 style="margin-top:0; color: #FF4B4B; font-size: 1.4rem;">{ev.get('title')}</h2>
        <p style="margin-bottom:8px; font-size: 1rem;"><b>📅 일시:</b> {ev.get('start').replace('T', ' ')}</p>
        <hr style="border: 0.5px solid #eee; margin: 15px 0;">
        <div style="background: #f1f1f1; padding: 12px; border-radius: 8px; font-size: 0.95rem; line-height: 1.5; color: #333;">
            {ev.get('extendedProps', {}).get('description', '상세 내용 없음')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("닫기", use_container_width=True):
        # 💡 닫을 때 카운터를 올려서 달력의 클릭 정보를 초기화시킴
        st.session_state.reset_count += 1
        st.session_state.last_processed_click = None
        st.rerun()

# --- 4. 🎨 스타일 최적화 ---
st.markdown("""
<style>
    .main-title { font-size: 1.8rem; font-weight: 800; text-align: center; color: #FF4B4B; margin-bottom: 0px; }
    .sub-title { text-align: center; color: #666; margin-bottom: 20px; font-size: 0.85rem; }
    div[data-testid="stDialog"] div[role="dialog"] {
        display: flex !important; flex-direction: column !important;
        justify-content: center !important; margin: auto !important;
        top: 50% !important; left: 50% !important;
        transform: translate(-50%, -50%) !important;
        position: fixed !important; width: 95% !important; max-width: 420px !important;
    }
    .fc-day-sun .fc-col-header-cell-cushion, .fc-day-sun .fc-daygrid-day-number { color: #FF4B4B !important; text-decoration: none; }
    .fc-day-sat .fc-col-header-cell-cushion, .fc-day-sat .fc-daygrid-day-number { color: #3133DE !important; text-decoration: none; }
    .fc-event-title { font-size: 0.72rem !important; font-weight: 600 !important; white-space: normal !important; }
</style>
<div class="main-title">🇯🇵 일본사는사람들</div>
<div class="sub-title">생일 & 정모 일정 달력</div>
""", unsafe_allow_html=True)

# --- 5. 🚀 일정 등록 섹션 ---
with st.expander("📅 새 일정 등록", expanded=False):
    input_pw = st.text_input("비밀번호", type="password", key="main_pw")
    if input_pw in ["144", ADMIN_PASSWORD]:
        tab1, tab2 = st.tabs(["🍺 정모 등록", "🎉 생일 등록"])
        with tab1:
            with st.form("form_meeting", clear_on_submit=True):
                date = st.date_input("날짜", datetime.date.today())
                time = st.time_input("시간", datetime.time(18, 0))
                title = st.text_input("정모 제목")
                location = st.text_input("위치")
                content = st.text_area("설명")
                if st.form_submit_button("등록", use_container_width=True):
                    if title:
                        st.session_state.events.append({
                            "title": f"🍺 {title}", "start": f"{date}T{time}",
                            "description": f"📍 위치: {location}\n📝 내용: {content}", "backgroundColor": "#FF4B4B"
                        })
                        save_data(st.session_state.events)
                        st.rerun()
        with tab2:
            with st.form("form_bday", clear_on_submit=True):
                bday_select = st.date_input("생일 날짜", datetime.date.today())
                name = st.text_input("성함")
                if st.form_submit_button("등록", use_container_width=True):
                    if name:
                        m, d = bday_select.month, bday_select.day
                        st.session_state.events.append({
                            "title": f"🎉 {name}", "start": f"{current_year}-{str(m).zfill(2)}-{str(d).zfill(2)}",
                            "rrule": f"FREQ=YEARLY;BYMONTH={m};BYMONTHDAY={d}",
                            "description": f"🎂 {name}님의 생일을 축하합니다!", "backgroundColor": "#FFD700", "allDay": True
                        })
                        save_data(st.session_state.events)
                        st.rerun()

# --- 6. 🗓️ 캘린더 표시 ---
calendar_options = {
    "headerToolbar": {"left": "prev,next", "center": "title", "right": "today"},
    "initialView": "dayGridMonth", "locale": "ko", "height": "auto", "aspectRatio": 0.85,
}

# 💡 [중요] reset_count를 key에 포함시켜 팝업을 닫을 때마다 달력을 초기화합니다.
state = calendar(
    events=st.session_state.events, 
    options=calendar_options, 
    key=f"calendar_v{st.session_state.reset_count}"
)

# --- 7. 🔥 클릭 이벤트 처리 ---
current_click = state.get("eventClick")

if current_click:
    click_id = f"{current_click['event']['title']}_{current_click['event']['start']}"
    
    # 💡 팝업을 띄우는 조건
    if st.session_state.last_processed_click != click_id:
        st.session_state.last_processed_click = click_id
        open_popup(current_click['event'])

# --- 8. 🗑️ 사이드바 ---
with st.sidebar:
    st.header("⚙️ 관리")
    admin_pw = st.text_input("관리자 비번", type="password", key="side_pw")
    if admin_pw == ADMIN_PASSWORD:
        if st.session_state.events:
            event_list = [f"{idx}: {ev['title']}" for idx, ev in enumerate(st.session_state.events)]
            target = st.selectbox("지울 일정", event_list)
            if st.button("삭제", type="primary"):
                idx = int(target.split(":")[0])
                st.session_state.events.pop(idx)
                save_data(st.session_state.events)
                st.session_state.reset_count += 1 # 삭제 후에도 달력 리셋
                st.rerun()