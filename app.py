import streamlit as st
from streamlit_calendar import calendar
import datetime
import json
import os

# --- 페이지 설정 및 모바일 최적화 Meta 태그 ---
st.set_page_config(
    page_title="🇯🇵 일본사는사람들 일정",
    layout="wide",
    initial_sidebar_state="collapsed", # 모바일에서 사이드바 숨김 시작
)

# --- 데이터 저장/로드 함수 (기존과 동일) ---
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

# --- 🔥 모바일 최적화 전용 고강도 CSS ---
mobile_css = """
<style>
    /* 1. 기본 텍스트 및 레이아웃 최적화 */
    .stApp { max-width: 100%; }
    .main .block-container { padding: 1rem 0.5rem; } /* 메인 여백 축소 */
    h1 { font-size: 1.8rem !important; text-align: center; margin-bottom: 0.5rem; } /* 제목 크기 축소 */
    .stMarkdown p { font-size: 0.9rem; } /* 안내문 폰트 축소 */

    /* 2. 캘린더 모바일 전용 스타일 (FullCalendar) */
    /* 헤더 툴바 (오늘, <, > 버튼) 최적화 */
    .fc-header-toolbar { 
        display: flex; flex-wrap: wrap; justify-content: center; gap: 5px; 
        margin-bottom: 0.5rem !important; 
    }
    .fc-toolbar-chunk { display: flex; align-items: center; }
    .fc-toolbar-title { font-size: 1.1rem !important; margin: 0 0.5rem !important; }
    
    /* 버튼 크기 키우기 (터치 용이성) */
    .fc-button { 
        padding: 0.4rem 0.6rem !important; font-size: 0.85rem !important; 
        min-width: 40px; 
    }

    /* 달력 본체 스타일 */
    .fc-view-harness { height: auto !important; } /* 높이 자동 조정 */
    .fc-daygrid-body { font-size: 0.8rem !important; } /* 날짜 숫자 크기 축소 */
    .fc-col-header-cell-cushion { font-size: 0.85rem !important; font-weight: 700 !important; } /* 요일 폰트 가독성 */
    
    /* 이벤트(일정) 바 스타일 */
    .fc-event { 
        font-size: 0.75rem !important; padding: 1px 3px !important; 
        margin: 1px 0 !important; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; 
    }

    /* 토/일 폰트 색상 (기존 유지) */
    .fc-day-sun .fc-col-header-cell-cushion, .fc-day-sun .fc-daygrid-day-number { color: #FF4B4B !important; text-decoration: none; }
    .fc-day-sat .fc-col-header-cell-cushion, .fc-day-sat .fc-daygrid-day-number { color: #3133DE !important; text-decoration: none; }

    /* 3. 사이드바(입력 폼) 모바일 최적화 */
    .css-163utfM { padding: 1.5rem 1rem !important; } /* 사이드바 여백 축소 */
    .stNumberInput div div input { font-size: 1rem !important; } /* 숫자 입력칸 크기 확대 */
    .stTextInput input, .stTextArea textarea, .stSelectbox div div div { font-size: 1rem !important; } /* 입력 필드 폰트 확대 */
    .stButton button { width: 100%; font-size: 1rem !important; padding: 0.5rem !important; } /* 버튼 꽉 차게 */

    /* 모바일 화면(폭 768px 이하) 전용 미디어 쿼리 */
    @media (max-width: 768px) {
        .fc-daygrid-day-frame { min-height: 50px !important; } /* 날짜 칸 높이 축소 */
        .fc-scroller-harness { overflow: hidden !important; }
        /* 생일 월/일 입력칸 레이아웃 조정 */
        .row-widget.stHorizontal { flex-direction: column; }
        .row-widget.stHorizontal > div { width: 100% !important; margin-bottom: 0.5rem; }
    }
</style>
"""
st.markdown(mobile_css, unsafe_allow_html=True)

# --- UI 레이아웃 ---
st.title("🇯🇵 일본사는사람들 일정")
st.markdown("<p style='text-align:center;color:gray;'>생일 & 정모 달력입니다</p>", unsafe_allow_html=True)
# st.markdown("---") # 모바일에서는 간결함을 위해 생략

with st.sidebar:
    st.header("🔐 권한 인증")
    input_pw = st.text_input("비밀번호 입력", type="password")
    
    if input_pw == "144" or input_pw == ADMIN_PASSWORD:
        st.success("인증 완료: 일정 등록 가능")
        category = st.selectbox("일정 종류 선택", ["정모", "생일"])
        
        with st.form("event_form", clear_on_submit=True):
            if category == "정모":
                date = st.date_input("날짜", datetime.date.today())
                time = st.time_input("시간", datetime.time(18, 0))
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
                    save_data(st.session_state.events)
                    st.rerun()
                    
            else: # 생일 등록
                col1, col2 = st.columns(2)
                with col1:
                    month = st.number_input("월", min_value=1, max_value=12, value=datetime.date.today().month)
                with col2:
                    day = st.number_input("일", min_value=1, max_value=31, value=datetime.date.today().day)
                
                name = st.text_input("성함")
                submit = st.form_submit_button("생일 등록")
                
                if submit and name:
                    try:
                        str_month = str(month).zfill(2)
                        str_day = str(day).zfill(2)
                        new_event = {
                            "title": f"🎉 {name}님", # 모바일 가독성을 위해 "생일" 생략
                            "start": f"{current_year}-{str_month}-{str_day}",
                            "rrule": f"FREQ=YEARLY;BYMONTH={month};BYMONTHDAY={day}",
                            "backgroundColor": "#FFD700",
                            "allDay": True
                        }
                        st.session_state.events.append(new_event)
                        save_data(st.session_state.events)
                        st.success(f"{name}님 저장!")
                        st.rerun()
                    except ValueError:
                        st.error("잘못된 날짜입니다.")

    if input_pw == ADMIN_PASSWORD:
        st.markdown("---")
        st.subheader("🗑️ 일정 삭제")
        if st.session_state.events:
            event_list = [f"{idx}: {ev['title']} ({ev.get('start', '매년')})" for idx, ev in enumerate(st.session_state.events)]
            target = st.selectbox("지울 일정", event_list)
            if st.button("삭제하기", type="primary"):
                idx = int(target.split(":")[0])
                st.session_state.events.pop(idx)
                save_data(st.session_state.events)
                st.rerun()

# --- 캘린더 표시 (반응형 설정 적용) ---
calendar_options = {
    "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listWeek"},
    "initialView": "dayGridMonth",
    "locale": "ko",
    "height": "auto", # 높이 자동 조정
    "aspectRatio": 1.2, # 모바일에서 더 세로로 길게 보이도록 조정
    "navLinks": True, # 날짜 클릭 시 일간 뷰 이동 가능
    "editable": False, # 드래그 앤 드롭 끄기
    "selectable": True, # 날짜 선택 가능
    "nowIndicator": True, # 현재 시간 표시
}

calendar(events=st.session_state.events, options=calendar_options)

st.info("💡 모바일에서는 오른쪽 상단의 '>' 버튼을 누르면 일정을 등록할 수 있습니다.")