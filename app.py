import streamlit as st
from streamlit_calendar import calendar
import datetime
import json
import os

# 페이지 설정
st.set_page_config(page_title="일본사는사람들 일정 관리", layout="wide")

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

# 세션 상태에 데이터 로드 (처음 한 번만)
if "events" not in st.session_state:
    st.session_state.events = load_data()

ADMIN_PASSWORD = "admin144" 
current_year = datetime.date.today().year

# --- UI 레이아웃 ---
st.title("🇯🇵 일본사는사람들 생일 & 정모 일정")
st.markdown("---")

with st.sidebar:
    st.header("🔐 권한 인증")
    input_pw = st.text_input("비밀번호를 입력하세요", type="password")
    
    if input_pw == "144" or input_pw == ADMIN_PASSWORD:
        st.success("인증 완료: 일정 등록 가능")
        category = st.selectbox("어떤 일정을 등록할까요?", ["정모", "생일"])
        
        with st.form("event_form", clear_on_submit=True):
            if category == "정모":
                date = st.date_input("정모 날짜", datetime.date.today())
                time = st.time_input("정모 시간", datetime.time(18, 0))
                title = st.text_input("정모 제목")
                location = st.text_input("상세 위치")
                content = st.text_area("모임 설명")
                submit = st.form_submit_button("정모 등록")
                
                if submit and title:
                    new_event = {
                        "title": f"🍺 {title}",
                        "start": f"{date}T{time}",
                        "description": f"위치: {location}\n내용: {content}",
                        "backgroundColor": "#FF4B4B",
                        "allDay": False
                    }
                    st.session_state.events.append(new_event)
                    save_data(st.session_state.events) # 파일 저장
                    st.rerun()
                    
            else: # 생일 등록
                col1, col2 = st.columns(2)
                with col1:
                    month = st.number_input("월", min_value=1, max_value=12, value=datetime.date.today().month)
                with col2:
                    day = st.number_input("일", min_value=1, max_value=31, value=datetime.date.today().day)
                
                name = st.text_input("생일자 성함")
                submit = st.form_submit_button("생일 등록")
                
                if submit and name:
                    try:
                        str_month = str(month).zfill(2)
                        str_day = str(day).zfill(2)
                        new_event = {
                            "title": f"🎉 {name}님 생일",
                            "start": f"{current_year}-{str_month}-{str_day}",
                            "rrule": f"FREQ=YEARLY;BYMONTH={month};BYMONTHDAY={day}",
                            "backgroundColor": "#FFD700",
                            "allDay": True
                        }
                        st.session_state.events.append(new_event)
                        save_data(st.session_state.events) # 파일 저장
                        st.success(f"{name}님의 생일이 저장되었습니다!")
                        st.rerun()
                    except ValueError:
                        st.error("올바르지 않은 날짜입니다.")

    if input_pw == ADMIN_PASSWORD:
        st.markdown("---")
        st.subheader("🗑️ 일정 삭제 (관리자 전용)")
        if st.session_state.events:
            event_list = [f"{idx}: {ev['title']} ({ev.get('start', '매년')})" for idx, ev in enumerate(st.session_state.events)]
            target = st.selectbox("지울 일정을 선택하세요", event_list)
            if st.button("삭제하기", type="primary"):
                idx = int(target.split(":")[0])
                st.session_state.events.pop(idx)
                save_data(st.session_state.events) # 파일 저장
                st.rerun()

# --- 캘린더 표시 ---
calendar_options = {
    "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listWeek"},
    "initialView": "dayGridMonth",
    "locale": "ko",
}

custom_css = """
    .fc-day-sun .fc-col-header-cell-cushion, .fc-day-sun .fc-daygrid-day-number { color: #FF4B4B !important; text-decoration: none; }
    .fc-day-sat .fc-col-header-cell-cushion, .fc-day-sat .fc-daygrid-day-number { color: #3133DE !important; text-decoration: none; }
"""

calendar(events=st.session_state.events, options=calendar_options, custom_css=custom_css)