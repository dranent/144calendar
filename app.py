import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from streamlit_calendar import calendar

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="🇯🇵 일본사는사람들 일정", layout="wide")

# --- 2. 구글 스프레드시트 연결 ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(ttl=0)
        df = df.fillna("")
        
        # [해결 1] allDay 타입을 확실하게 정리
        if 'allDay' in df.columns:
            df['allDay'] = df['allDay'].apply(lambda x: True if str(x).upper() == 'TRUE' else False)
        
        return df
    except:
        return pd.DataFrame(columns=["title", "start", "description", "backgroundColor", "allDay", "rrule"])

def save_data(df):
    conn.update(data=df)

# 데이터 로드
df_events = load_data()

# 💡 [핵심 해결 2] rrule이 빈 문자열인 경우 아예 제외하고 리스트 만들기
# rrule: "" 라고 보내면 캘린더가 뻗기 때문에 키 자체를 없애야 합니다.
events_list = []
for _, row in df_events.iterrows():
    ev = row.to_dict()
    # rrule이 비어있거나(None) 빈 문자열("")이면 키 삭제
    if not ev.get("rrule") or ev.get("rrule") == "":
        ev.pop("rrule", None)
    events_list.append(ev)

ADMIN_PASSWORD = "admin144"
current_year = datetime.date.today().year
# --- 3. 🔍 상세 정보 팝업 (시간 표시 로직 수정) ---
@st.dialog("🔍 일정 상세 정보")
def open_popup(ev):
    title = ev.get('title', '제목 없음')
    is_all_day = ev.get('allDay', False)
    raw_start = ev.get('start', '')
    
    # 💡 [핵심] 하루 종일 일정(생일 등)은 날짜만, 시간 일정(정모 등)은 시간까지 표시
    if is_all_day:
        # T 이후의 시간 정보를 자르고 날짜만 추출
        start_val = str(raw_start).split('T')[0]
        date_label = "📅 날짜"
    else:
        # T를 공백으로 바꿔서 시간까지 표시
        start_val = str(raw_start).replace('T', ' ')
        date_label = "⏰ 일시"
        
    desc = ev.get('description', '상세 내용 없음')
    
    st.markdown(f"""
    <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; color: #1e1e1e; border: 1px solid #ddd;">
        <h2 style="margin-top:0; color: #FF4B4B; font-size: 1.4rem;">{title}</h2>
        <p style="margin-bottom:8px;"><b>{date_label}:</b> {start_val}</p>
        <hr style="border: 0.5px solid #eee; margin: 15px 0;">
        <div style="background: #f1f1f1; padding: 12px; border-radius: 8px; font-size: 0.95rem; color: #333;">
            {desc}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 사용자의 요청대로 하단 닫기 버튼은 삭제되었습니다. 
    # 창 밖을 클릭하거나 우측 상단 X를 눌러 닫으시면 됩니다.
# --- 4. 🎨 스타일 최적화 ---
st.markdown("""
<style>
    .main-title { font-size: 1.8rem; font-weight: 800; text-align: center; color: #FF4B4B; margin: 0; }
    .sub-title { text-align: center; color: #666; margin-bottom: 20px; font-size: 0.85rem; }
    div[data-testid="stDialog"] div[role="dialog"] {
        top: 50% !important; left: 50% !important; transform: translate(-50%, -50%) !important;
        position: fixed !important; width: 95% !important; max-width: 420px !important;
    }
</style>
<div class="main-title">🇯🇵 일본사는사람들</div>
<div class="sub-title">생일 & 정모 일정 달력</div>
""", unsafe_allow_html=True)

# --- 5. 🚀 일정 등록 섹션 ---
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
                    if title:
                        new_row = pd.DataFrame([{
                            "title": f"🍺 {title}", "start": f"{date}T{time}",
                            "description": f"📍 위치: {location}\n📝 내용: {content}",
                            "backgroundColor": "#FF4B4B", "allDay": False, "rrule": "" 
                        }])
                        save_data(pd.concat([df_events, new_row], ignore_index=True))
                        st.rerun()

        with tab2:
            with st.form("form_bday"):
                col1, col2 = st.columns(2)
                with col1: month = st.selectbox("월", range(1, 13), index=datetime.date.today().month - 1)
                with col2: day = st.selectbox("일", range(1, 32), index=datetime.date.today().day - 1)
                name = st.text_input("성함")
                if st.form_submit_button("등록", use_container_width=True):
                    if name:
                        try:
                            datetime.date(current_year, month, day)
                            new_row = pd.DataFrame([{
                                "title": f"🎉 {name}", 
                                "start": f"{current_year}-{str(month).zfill(2)}-{str(day).zfill(2)}",
                                "description": f"🎂 {name}님의 생일을 축하합니다!",
                                "backgroundColor": "#FFD700", "allDay": True,
                                "rrule": f"FREQ=YEARLY;BYMONTH={month};BYMONTHDAY={day}"
                            }])
                            save_data(pd.concat([df_events, new_row], ignore_index=True))
                            st.rerun()
                        except ValueError:
                            st.error("존재하지 않는 날짜입니다!")

# --- 6. 🗓️ 캘린더 표시 ---
# 데이터 길이에 연동된 가변 Key 사용 (상태 초기화용)
cal_key = f"japan_calendar_{len(events_list)}"

# 💡 [핵심] 달력 옵션에서 displayEventTime을 False로 설정하여 칸 내부의 시간 표시를 숨깁니다.
calendar_options = {
    "headerToolbar": {"left": "prev,next", "center": "title", "right": "today"},
    "initialView": "dayGridMonth",
    "locale": "ko",
    "height": "auto",
    "aspectRatio": 0.85,
    "displayEventTime": False  # ✅ 이 줄을 추가하세요! 달력 칸에서 00:00 같은 표시가 사라집니다.
}

state = calendar(
    events=events_list, 
    options=calendar_options, 
    key=cal_key
)

if state and state.get("eventClick"):
    open_popup(state["eventClick"]["event"])

# --- 7. 🗑️ 관리자 삭제 메뉴 ---
with st.sidebar:
    if st.text_input("관리자 비번", type="password", key="side_pw") == ADMIN_PASSWORD:
        if not df_events.empty:
            target_idx = st.selectbox("지울 일정", df_events.index, format_func=lambda x: df_events.loc[x, 'title'])
            if st.button("삭제하기"):
                df_events = df_events.drop(target_idx)
                save_data(df_events)
                st.rerun()