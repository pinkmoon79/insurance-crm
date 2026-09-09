import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse
import datetime

# 1. 페이지 레이아웃 세팅
st.set_page_config(page_title="PRO-PIPE MASTER CRM", page_icon="🛡️", layout="wide")

# 2. 토스 스타일의 프리미엄 UI 및 타임라인 CSS
st.markdown("""
    <style>
        @import url('https://googleapis.com');
        * { font-family: 'Inter', 'Noto Sans KR', sans-serif; }
        .stApp { background-color: #0B0F19; color: #F8FAFC; }
        [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1F2937; }
        .premium-card {
            background-color: #1F2937; padding: 20px; border-radius: 16px;
            border: 1px solid #374151; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); margin-bottom: 15px;
        }
        .metric-title { color: #9CA3AF; font-size: 13px; font-weight: 500; }
        .metric-value { color: #FFFFFF; font-size: 26px; font-weight: 700; margin-top: 4px; }
        .cust-row { background-color: #111827; padding: 20px; border-radius: 12px; border: 1px solid #1F2937; margin-bottom: 12px; }
        .badge-id { background-color: #374151; color: #9CA3AF; padding: 2px 6px; border-radius: 4px; font-size: 11px; }
        .badge-region { background-color: #1E3A8A; color: #3B82F6; padding: 3px 8px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .badge-update { background-color: #7F1D1D; color: #F87171; padding: 3px 8px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .kakaotalk-btn-style {
            display: inline-block; width: 100%; text-align: center; background-color: #FEE500; color: #191919;
            padding: 12px 20px; border-radius: 10px; font-size: 15px; font-weight: 700; text-decoration: none; margin-top: 10px;
        }
        /* AI 타임라인 박스 */
        .timeline-box {
            background-color: #1E2937; border-left: 4px solid #10B981; padding: 12px; margin-top: 8px; border-radius: 0px 8px 8px 0px;
        }
    </style>
""", unsafe_allow_html=True)

# 3. 데이터베이스(DB) 세팅 (고객 테이블 & AI 메모 테이블 분리)
def init_db():
    conn = sqlite3.connect('pro_pipe_ultimate.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY, name TEXT, phone TEXT, wide_region TEXT, detail_region TEXT,
            cancer_cover INTEGER, stroke_cover INTEGER, status TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id TEXT, note_type TEXT, content TEXT, date TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- 사이드바 통제 센터 ---
with st.sidebar:
    st.markdown("<h2 style='color:#3B82F6;'>⚙️ PRO-PIPE CRM</h2>", unsafe_allow_html=True)
    st.caption("24시간 상시 가동 성공 무기")
    st.write("---")
    market_event = st.selectbox("🚨 최신 보장 트렌드 (상향 근거)", ["선택 없음", "🔥 뇌혈관 질환 보장 한도 5,000만원 상향", "💥 암 진단비 최소 5,000만원 업계 필수 표준화"])
    target_region = st.selectbox("📍 내일 방문할 출장 권역", ["서울/수도권", "부산/영남권", "대전/충청권", "광주/호남권"])
    travel_date = st.date_input("📅 출장 날짜 설정", datetime.date.today() + datetime.timedelta(days=1))

# --- 메인 화면 레이아웃 (좌: 데이터 입력/업로드 | 우: 실시간 관제 및 카톡 발송) ---
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.markdown("### 📥 데이터 입력 및 AI 비서 노트 피드")
    
    # 탭 메뉴로 입력 분리
    input_tab1, input_tab2 = st.tabs(["📊 사내 전산 엑셀 등록", "🎙️ 갤럭시AI/에이닷 요약본 등록"])
    
    with input_tab1:
        uploaded_file = st.file_uploader("전산 다운로드 엑셀 파일(.xlsx/.csv)", type=["csv", "xlsx"])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                if st.button("💾 장부에 대량 등록 실행", key="bulk_btn"):
                    conn = sqlite3.connect('pro_pipe_ultimate.db')
                    cursor = conn.cursor()
                    for idx, row in df.iterrows():
                        cursor.execute("INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, '정상 유지')",
                                       (str(row['고객번호']), str(row['이름']), str(row['연락처']), str(row['거주권역']), str(row['상세주소']), int(row['기존암진단비']), int(row['기존뇌진단비'])))
                    conn.commit()
                    conn.close()
                    st.success("🎉 대량 등록이 완료되었습니다!")
            except Exception as e:
                st.error(f"양식을 확인해 주세요: {e}")
                
    with input_tab2:
        st.write("스마트폰 AI 비서(갤럭시/에이닷)가 요약해 준 대화나 카톡 내용을 저장합니다.")
        conn = sqlite3.connect('pro_pipe_ultimate.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, phone FROM customers")
        all_custs = cursor.fetchall()
        conn.close()
        
        if not all_custs:
            st.info("메모를 등록할 기존 고객이 없습니다. 엑셀을 먼저 업로드해 주세요.")
        else:
            cust_options = {f"{c[1]} ({c[2][-4:]})": c[0] for c in all_custs}
            selected_cust_name = st.selectbox("🎯 메모를 등록할 고객 선택", list(cust_options.keys()))
            selected_cust_id = cust_options[selected_cust_name]
            
            note_type = st.radio("소통 종류", ["🎙️ 통화 녹음 AI 요약", "💬 카톡/문자 주요 내용"])
            ai_text = st.text_area("AI 비서 요약문 붙여넣기 (Ctrl + V)", placeholder="예: '어제 내과 방문 서류 실비 청구 요청함'")
            
            if st.button("💾 고객 타임라인에 AI 메모 저장"):
                conn = sqlite3.connect('pro_pipe_ultimate.db')
                cursor = conn.cursor()
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                cursor.execute("INSERT INTO ai_notes (customer_id, note_type, content, date) VALUES (?, ?, ?, ?)",
                               (selected_cust_id, note_type, ai_text, now_str))
                conn.commit()
                conn.close()
                st.success("🧠 AI 비서 기록이 고객 타임라인에 누적되었습니다!")

with col_right:
    st.markdown("### 📊 실시간 보장 분석 및 카카오톡 대기열")
    
    conn = sqlite3.connect('pro_pipe_ultimate.db')
    cursor = conn.cursor()
    
    # 상향 엔진 로직
    if market_event == "🔥 뇌혈관 질환 보장 한도 5,000만원 상향":
        cursor.execute("UPDATE customers SET status = '🚨 뇌보장 업셀링 대상' WHERE stroke_cover < 3000")
        conn.commit()
    elif market_event == "💥 암 진단비 최소 5,000만원 업계 필수 표준화":
        cursor.execute("UPDATE customers SET status = '🚨 암보장 업셀링 대상' WHERE cancer_cover < 5000")
        conn.commit()
    else:
        cursor.execute("UPDATE customers SET status = '정상 유지'")
        conn.commit()
        
    cursor.execute("SELECT * FROM customers WHERE wide_region = ?", (target_region,))
    db_customers = cursor.fetchall()
    
    if not db_customers:
        st.info(f"현재 [{target_region}] 권역에 매칭된 고객이 없습니다. 엑셀 등록 후 가동해 보세요!")
    else:
        for cust in db_customers:
            c_id, c_name, c_phone, c_wide, c_detail, c_cancer, c_stroke, c_status = cust
            badge_style = f"<span class='badge-update'>{c_status}</span>" if "업셀링" in c_status else f"<span class='badge-region'>{c_status}</span>"
            
            st.markdown(f"""
                <div class="cust-row">
                    <span style="font-size:17px; font-weight:700; color:#FFF;">{c_name}</span> &nbsp;<span class="badge-id">{c_id}</span> &nbsp;{badge_style}<br>
                    <small style="color:#9CA3AF;">📍 동선 주소: {c_detail} | 📱 {c_phone}</small><br>
                    <small style="color:#38BDF8;">📉 엑셀 등록 보장: 암 {c_cancer}만원 / 뇌 {c_stroke}만원</small>
            """, unsafe_allow_html=True)
            
            # 🌟 해당 고객에게 누적된 AI 비서 메모(타임라인)가 있다면 하단에 실시간 출력
            cursor.execute("SELECT note_type, content, date FROM ai_notes WHERE customer_id = ? ORDER BY id DESC", (c_id,))
            notes = cursor.fetchall()
            for n_type, n_content, n_date in notes:
                st.markdown(f"""
                    <div class="timeline-box">
                        <small style="color:#10B981; font-weight:bold;">{n_type}</small> <small style="color:#9CA3AF;">({n_date})</small><br>
                        <span style="font-size:13px; color:#E5E7EB;">{n_content}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True) # 카드 닫기
            
            # 카톡 발송 로직 조립
            src_fact = "금융감독원 및 보험협회 최신 공시 개정 표준 반영"
            if "업셀링" in c_status:
                msg = f"[{c_name} 고객님 기존 보장 상향 안내]\n\n안녕하세요, 담당 설계사입니다. 전산 분석 결과에 따라 안내 드립니다.\n\n📊 가입 분석 결과:\n- 최신 업계 표준: 최소 5,000만 원 보장 권장\n- 근거 데이터: {src_fact}\n- ❌ 고객님 기존 금액: 암 {c_cancer}만 / 뇌 {c_stroke}만 (보장 공백 발생)\n\n제가 {travel_date}에 {c_wide} 출장 가는 길에 상향 보완된 맞춤 설계안을 전해드리고자 합니다. 아래 링크에서 편하신 미팅 시간을 확정해 주세요!\n🔗 링크: https://pro-pipe.app{c_id}"
            else:
                msg = f"[{c_name} 고객님 안부 인사]\n\n안녕하세요, 담당 설계사입니다. {travel_date}에 {c_wide} 출장이 있어 연락드렸습니다. 현재 보장 상태는 안정적이나 정기 점검차 잠시 뵙고자 합니다. 아래 링크에서 시간을 골라주세요!\n🔗 링크: https://pro-pipe.app{c_id}"
            
            encoded_msg = urllib.parse.quote(msg)
            share_url = f"https://kakao.com{encoded_msg}"
            st.markdown(f'<a href="{share_url}" target="_blank" class="kakaotalk-btn-style">💬 {c_name} 고객에게 상향 권유 카톡 쏘기</a>', unsafe_allow_html=True)
            st.write("")
            
    conn.close()
