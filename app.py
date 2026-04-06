import streamlit as st
from streamlit_calendar import calendar
import datetime
import json
import os

# --- 페이지 설정 ---
st.set_page_config(
    page_title="🇯🇵 일본사는사람들 일정",
    layout="wide",
)

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

# --- 🎨 모바일 최적화 및 UI 개선 CSS ---
st.markdown("""
<style>
    /* 메인 타이틀 디자인 */
    .main-title { font-size: 2rem; font-weight: 800; text-align: center; color: #FF4B4B; margin-bottom: 0px; }
    .sub-title { text-align: center; color: #666; margin-bottom: 20px; }
    
    /* 캘린더 날짜 색상 */
    .fc-day-sun .fc-col-header-cell-cushion, .fc-day-sun .fc-daygrid-day-number { color: #FF4B4B !important; text-decoration: none; }
    .fc-day-sat .fc-col-header-cell-cushion, .fc-day-sat .fc-daygrid-day-number { color: #3133DE !important; text-decoration: none; }
    
    /* 입력 폼 가시성 강화 */
    .stExpander { border: 2px solid #FF4B4B !important; border-radius: 10px !important; }
</style>
<div class="main-title">🇯🇵 일본사는사람들</div>
<div class="sub-title">생일 & 정모 일정 달력</div>
""", unsafe_allow_html=True)

# --- 🚀 메인 화면 상단: 일정 등록 섹션 ---
# 사이드바 대신 메인 화면에 배치하여 접근성 강화
with st.expander("📅 여기를 눌러 새 일정을 등록하세요!", expanded=False):
    input_pw = st.text_input("비밀번호", type="password", key="main_pw")
    
    if input_pw == "144" or input_pw == ADMIN_PASSWORD:
        category = st.radio("일정 종류", ["정모 🍺", "생일 🎉"], horizontal=True)
        
        with st.form("main_event_form", clear_on_submit=True):
            if "정모" in category:
                date = st.date_input("날짜", datetime.date.today())
                time = st.time_input("시간", datetime.time(18, 0))
                title = st.text_input("정모 제목")
                location = st.text_input("상세 위치")
                submit = st.form_submit_button("정모 일정 등록하기", use_container_width=True)
                
                if submit and title:
                    st.session_state.events.append({
                        "title": f"🍺 {title}",
                        "start": f"{date}T{time}",
                        "backgroundColor": "#FF4B4B",
                    })
                    save_data(st.session_state.events)
                    st.success("등록 완료!")
                    st.rerun()
            else:
                col1, col2 = st.columns(2)
                with col1: month = st.number_input("월", 1, 12, datetime.date.today().month)
                with col2: day = st.number_input("일", 1, 31, datetime.date.today().day)
                name = st.text_input("생일자 성함")
                submit = st.form_submit_button("생일 등록하기", use_container_width=True)
                
                if submit and name:
                    try:
                        st.session_state.events.append({
                            "title": f"🎉 {name}님",
                            "start": f"{current_year}-{str(month).zfill(2)}-{str(day).zfill(2)}",
                            "rrule": f"FREQ=YEARLY;BYMONTH={month};BYMONTHDAY={day}",
                            "backgroundColor": "#FFD700",
                            "allDay": True
                        })
                        save_data(st.session_state.events)
                        st.success(f"{name}님 저장 완료!")
                        st.rerun()
                    except: st.error("날짜 확인!")
    elif input_pw != "":
        st.error("비밀번호가 틀렸습니다.")

# --- 🗑️ 사이드바: 관리자 전용 삭제 메뉴 ---
with st.sidebar:
    st.header("⚙️ 관리 전용")
    admin_pw = st.text_input("관리자 비밀번호", type="password", key="side_pw")
    if admin_pw == ADMIN_PASSWORD:
        st.subheader("🗑️ 일정 삭제")
        if st.session_state.events:
            event_list = [f"{idx}: {ev['title']} ({ev.get('start', '매년')})" for idx, ev in enumerate(st.session_state.events)]
            target = st.selectbox("지울 일정", event_list)
            if st.button("삭제하기", type="primary"):
                idx = int(target.split(":")[0])
                st.session_state.events.pop(idx)
                save_data(st.session_state.events)
                st.rerun()
    else:
        st.info("관리자 비밀번호 입력 시 삭제 메뉴가 나타납니다.")

# --- 🗓️ 캘린더 표시 ---
calendar_options = {
    "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listWeek"},
    "initialView": "dayGridMonth",
    "locale": "ko",
    "height": "auto",
}

calendar(events=st.session_state.events, options=calendar_options)