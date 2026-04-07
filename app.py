import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- 페이지 설정 ---
st.set_page_config(page_title="🇯🇵 일본사는사람들 일정", layout="wide")

# --- 💡 구글 스프레드시트 연결 설정 ---
# 시트 주소: https://docs.google.com/spreadsheets/d/1WAgEOBu9QJqCrEk3h7fXOgnaH7BhVzHo93dDvl2UsIw/edit
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # 시트에서 데이터를 읽어옵니다. (첫 번째 시트 기준)
        return conn.read(ttl=0) # ttl=0은 캐시 없이 실시간 데이터를 가져옵니다.
    except:
        # 데이터가 아예 없으면 빈 데이터프레임 반환
        return pd.DataFrame(columns=["title", "start", "description", "backgroundColor", "allDay", "rrule"])

def save_data(df):
    # 구글 시트에 업데이트합니다.
    conn.update(data=df)

# 세션 상태에 데이터 로드
df_events = load_data()
# 캘린더용 리스트로 변환
events_list = df_events.to_dict(orient="records")

ADMIN_PASSWORD = "admin144"
current_year = datetime.date.today().year

# --- 🔍 팝업창 함수 (다크모드 대응) ---
@st.dialog("🔍 일정 상세 정보")
def open_popup(ev):
    st.markdown(f"""
    <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; color: #1e1e1e; border: 1px solid #ddd;">
        <h2 style="margin-top:0; color: #FF4B4B; font-size: 1.4rem;">{ev.get('title')}</h2>
        <p style="margin-bottom:8px;"><b>📅 일시:</b> {str(ev.get('start')).replace('T', ' ')}</p>
        <hr style="border: 0.5px solid #eee; margin: 15px 0;">
        <div style="background: #f1f1f1; padding: 12px; border-radius: 8px; font-size: 0.95rem; color: #333;">
            {ev.get('description', '상세 내용 없음')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("닫기", use_container_width=True):
        st.rerun()

# --- 🎨 스타일 및 CSS (기존 동일) ---
st.markdown("""
<style>
    .main-title { font-size: 1.8rem; font-weight: 800; text-align: center; color: #FF4B4B; margin: 0; }
    .sub-title { text-align: center; color: #666; margin-bottom: 20px; font-size: 0.85rem; }
    div[data-testid="stDialog"] div[role="dialog"] {
        top: 50% !important; left: 50% !important; transform: translate(-50%, -50%) !important;
        position: fixed !important; width: 95% !important; max-width: 420px !important;
    }
    .fc-day-sun .fc-col-header-cell-cushion, .fc-day-sun .fc-daygrid-day-number { color: #FF4B4B !important; }
    .fc-day-sat .fc-col-header-cell-cushion, .fc-day-sat .fc-daygrid-day-number { color: #3133DE !important; }
</style>
<div class="main-title">🇯🇵 일본사는사람들</div>
<div class="sub-title">생일 & 정모 일정 달력</div>
""", unsafe_allow_html=True)

# --- 🚀 일정 등록 섹션 ---
with st.expander("📅 새 일정 등록", expanded=False):
    input_pw = st.text_input("비밀번호", type="password", key="main_pw")
    if input_pw in ["144", ADMIN_PASSWORD]:
        tab1, tab2 = st.tabs(["🍺 정모", "🎉 생일"])
        
        with tab1:
            with st.form("form_meeting"):
                date = st.date_input("날짜", datetime.date.today())
                time = st.time_input("시간", datetime.time(18, 0))
                title = st.text_input("정모 제목")
                location = st.text_input("위치")
                content = st.text_area("설명")
                if st.form_submit_button("등록", use_container_width=True):
                    new_row = pd.DataFrame([{
                        "title": f"🍺 {title}", "start": f"{date}T{time}",
                        "description": f"📍 위치: {location}\n📝 내용: {content}",
                        "backgroundColor": "#FF4B4B", "allDay": False, "rrule": ""
                    }])
                    save_data(pd.concat([df_events, new_row], ignore_index=True))
                    st.success("구글 시트에 저장 완료!")
                    st.rerun()

        with tab2:
            with st.form("form_bday"):
                bday_select = st.date_input("생일 날짜", datetime.date.today())
                name = st.text_input("성함")
                if st.form_submit_button("등록", use_container_width=True):
                    m, d = bday_select.month, bday_select.day
                    new_row = pd.DataFrame([{
                        "title": f"🎉 {name}", "start": f"{current_year}-{str(m).zfill(2)}-{str(d).zfill(2)}",
                        "description": f"🎂 {name}님의 생일을 축하합니다!",
                        "backgroundColor": "#FFD700", "allDay": True,
                        "rrule": f"FREQ=YEARLY;BYMONTH={m};BYMONTHDAY={d}"
                    }])
                    save_data(pd.concat([df_events, new_row], ignore_index=True))
                    st.success("구글 시트에 저장 완료!")
                    st.rerun()

# --- 🗓️ 캘린더 표시 ---
from streamlit_calendar import calendar
state = calendar(events=events_list, options={"headerToolbar": {"left": "prev,next", "center": "title", "right": "today"}, "initialView": "dayGridMonth", "locale": "ko", "height": "auto", "aspectRatio": 0.85}, key="japan_calendar_gsheets")

if state.get("eventClick"):
    open_popup(state["eventClick"]["event"])

# --- 🗑️ 관리자 삭제 메뉴 ---
with st.sidebar:
    if st.text_input("관리자 비번", type="password") == ADMIN_PASSWORD:
        if not df_events.empty:
            target_idx = st.selectbox("지울 일정", df_events.index, format_func=lambda x: df_events.loc[x, 'title'])
            if st.button("삭제하기"):
                df_events = df_events.drop(target_idx)
                save_data(df_events)
                st.rerun()