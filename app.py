import streamlit as st
from streamlit_calendar import calendar
import datetime
import json
import os

# --- 페이지 설정 ---
st.set_page_config(page_title="🇯🇵 일본사는사람들 일정", layout="wide")

# --- 데이터 저장/로드 함수 ---
DB_FILE = "events.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(events):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=4)

if "events" not in st.session_state:
    st.session_state.events = load_data()

ADMIN_PASSWORD = "admin144" 
current_year = datetime.date.today().year

# --- 💡 팝업창(Dialog) 정의 (버튼 삭제 버전) ---
@st.dialog("🔍 일정 상세 정보")
def show_details(event):
    title = event.get("title", "제목 없음")
    st.subheader(title)
    
    # 시간 처리
    start_time = event.get("start", "")
    if "T" in start_time:
        dt = datetime.datetime.fromisoformat(start_time)
        st.write(f"⏰ **일시**: {dt.strftime('%Y년 %m월 %d일 %H:%M')}")
    else:
        st.write(f"📅 **날짜**: {start_time}")
    
    # 상세 내용
    props = event.get("extendedProps", {})
    desc = props.get("description", "상세 내용이 없습니다.")
    st.info(desc)
    st.caption("💡 창 밖을 누르거나 우측 상단 X를 눌러 닫으세요.")

# --- 🎨 UI 및 중앙 정렬 CSS ---
st.markdown("""
<style>
    /* 메인 타이틀 */
    .main-title { font-size: 2rem; font-weight: 800; text-align: center; color: #FF4B4B; margin-bottom: 0px; }
    .sub-title { text-align: center; color: #666; margin-bottom: 20px; }
    
    /* 주말 색상 */
    .fc-day-sun .fc-col-header-cell-cushion, .fc-day-sun .fc-daygrid-day-number { color: #FF4B4B !important; text-decoration: none; }
    .fc-day-sat .fc-col-header-cell-cushion, .fc-day-sat .fc-daygrid-day-number { color: #3133DE !important; text-decoration: none; }
    
    /* 🔴 팝업창(Dialog) 화면 중앙 배치 강제 설정 */
    div[data-testid="stDialog"] div[role="dialog"] {
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin: auto !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
    }
    
    /* 모바일에서 입력창 여백 조절 */
    .stExpander { border: 2px solid #FF4B4B !important; border-radius: 10px !important; }
</style>
<div class="main-title">🇯🇵 일본사는사람들</div>
<div class="sub-title">생일 & 정모 일정 달력</div>
""", unsafe_allow_html=True)

# --- 🚀 일정 등록 섹션 ---
with st.expander("📅 새 일정 등록", expanded=False):
    input_pw = st.text_input("비밀번호", type="password", key="main_pw")
    if input_pw in ["144", ADMIN_PASSWORD]:
        category = st.radio("일정 종류", ["정모 🍺", "생일 🎉"], horizontal=True)
        with st.form("main_event_form", clear_on_submit=True):
            if "정모" in category:
                date = st.date_input("날짜", datetime.date.today())
                time = st.time_input("시간", datetime.time(18, 0))
                title = st.text_input("정모 제목")
                location = st.text_input("상세 위치")
                content = st.text_area("내용 설명")
                submit = st.form_submit_button("정모 일정 등록하기", use_container_width=True)
                if submit and title:
                    st.session_state.events.append({
                        "title": f"🍺 {title}",
                        "start": f"{date}T{time}",
                        "description": f"📍 위치: {location}\n📝 내용: {content}",
                        "backgroundColor": "#FF4B4B",
                    })
                    save_data(st.session_state.events)
                    st.rerun()
            else:
                col1, col2 = st.columns(2)
                with col1: month = st.number_input("월", 1, 12, datetime.date.today().month)
                with col2: day = st.number_input("일", 1, 31, datetime.date.today().day)
                name = st.text_input("성함")
                submit = st.form_submit_button("생일 등록하기", use_container_width=True)
                if submit and name:
                    try:
                        st.session_state.events.append({
                            "title": f"🎉 {name}님",
                            "start": f"{current_year}-{str(month).zfill(2)}-{str(day).zfill(2)}",
                            "rrule": f"FREQ=YEARLY;BYMONTH={month};BYMONTHDAY={day}",
                            "description": f"🎂 {name}님의 생일을 축하합니다!",
                            "backgroundColor": "#FFD700",
                            "allDay": True
                        })
                        save_data(st.session_state.events)
                        st.rerun()
                    except: st.error("날짜 확인!")

# --- 🗓️ 캘린더 표시 ---
calendar_options = {
    "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listWeek"},
    "initialView": "dayGridMonth",
    "locale": "ko",
    "height": "auto",
}

# 캘린더 실행
state = calendar(events=st.session_state.events, options=calendar_options, key="japan_calendar_final")

# --- 🔥 클릭 시 팝업 호출 ---
if state.get("eventClick"):
    show_details(state["eventClick"]["event"])

# --- 🗑️ 사이드바 (삭제 메뉴) ---
with st.sidebar:
    st.header("⚙️ 관리 전용")
    admin_pw = st.text_input("관리자 비밀번호", type="password", key="side_pw")
    if admin_pw == ADMIN_PASSWORD:
        st.subheader("🗑️ 일정 삭제")
        if st.session_state.events:
            event_list = [f"{idx}: {ev['title']}" for idx, ev in enumerate(st.session_state.events)]
            target = st.selectbox("지울 일정", event_list)
            if st.button("삭제하기", type="primary"):
                idx = int(target.split(":")[0])
                st.session_state.events.pop(idx)
                save_data(st.session_state.events)
                st.rerun()