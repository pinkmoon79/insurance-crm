import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from urllib.parse import quote
import os

# ============================================================================
# 🎨 페이지 설정 및 스타일
# ============================================================================

st.set_page_config(
    page_title="보험 파이프라인 CRM",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 다크모드 CSS
st.markdown("""
<style>
    :root {
        --primary-bg: #0f1419;
        --secondary-bg: #1a202c;
        --accent-blue: #4a90e2;
        --accent-red: #ff4757;
        --text-primary: #ffffff;
    }
    
    body { background-color: var(--primary-bg) !important; }
    .stApp { background-color: var(--primary-bg) !important; }
    .stButton > button { background-color: var(--accent-blue) !important; color: white !important; }
    .badge-status { background-color: var(--accent-red); padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; }
    .customer-card { border: 1px solid #2d3748; padding: 16px; border-radius: 8px; margin: 8px 0; background-color: var(--secondary-bg); }
    .timeline-box { background-color: #0f1419; border-left: 3px solid var(--accent-blue); padding: 12px; margin: 8px 0; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 🛡️ 보안 로그인 (Streamlit Cloud 호환)
# ============================================================================

DB_PATH = "insurance_crm.db"

def init_database():
    """SQLite 데이터베이스 초기화"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 고객 정보 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT,
        phone TEXT,
        region TEXT,
        address TEXT,
        cancer_coverage REAL,
        brain_coverage REAL
    )
    """)
    
    # 상담 노트 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS consultation_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        note_type TEXT,
        content TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)
    
    conn.commit()
    conn.close()

# 로그인 상태 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ============================================================================
# 🔐 로그인 페이지
# ============================================================================

if not st.session_state.logged_in:
    st.markdown("## 🛡️ 보험 파이프라인 CRM - 보안 로그인")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        username = st.text_input("ID", placeholder="master", key="login_id")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pw")
        
        if st.button("🔓 로그인", use_container_width=True):
            # Streamlit Cloud에서는 st.secrets 사용, 로컬에서는 하드코드
            try:
                stored_id = st.secrets.get("master_id", "master")
                stored_pw = st.secrets.get("master_password", "pipe7979!")
            except:
                stored_id = "master"
                stored_pw = "pipe7979!"
            
            if username.strip() == stored_id and password.strip() == stored_pw:
                st.session_state.logged_in = True
                st.success("✅ 로그인 성공!")
                st.rerun()
            else:
                st.error("❌ ID 또는 비밀번호가 올바르지 않습니다.")

else:
    # ========================================================================
    # ✅ 메인 CRM 화면 (로그인 성공 후)
    # ========================================================================
    
    init_database()
    
    # 로그아웃 버튼
    if st.sidebar.button("🚪 로그아웃", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    
    st.markdown("## 🛡️ 보험 파이프라인 CRM 시스템")
    st.markdown("---")
    
    # ====================================================================
    # 【좌측】 데이터 관리
    # ====================================================================
    
    left_col, right_col = st.columns([1, 1.2], gap="large")
    
    with left_col:
        st.markdown("### 📥 데이터 입력 & 관리")
        
        tab1, tab2, tab3 = st.tabs(["엑셀 업로드", "상담 기록", "고객 현황"])
        
        # 탭 1: 엑셀 업로드
        with tab1:
            st.markdown("**표준 엑셀/CSV 파일 업로드**")
            st.info("필수 컬럼: 고객번호, 이름, 연락처, 거주권역, 상세주소, 기존암진단비, 기존뇌진단비")
            
            uploaded_file = st.file_uploader("파일 선택", type=["xlsx", "csv"])
            
            if uploaded_file:
                try:
                    if uploaded_file.name.endswith(".csv"):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                    
                    st.dataframe(df.head(), use_container_width=True)
                    
                    if st.button("🚀 데이터 병합하기", use_container_width=True):
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        
                        for _, row in df.iterrows():
                            customer_id = str(row['고객번호']).strip()
                            cursor.execute("""
                            INSERT OR REPLACE INTO customers 
                            (customer_id, name, phone, region, address, cancer_coverage, brain_coverage)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (
                                customer_id,
                                str(row['이름']).strip(),
                                str(row['연락처']).strip(),
                                str(row['거주권역']).strip(),
                                str(row['상세주소']).strip(),
                                float(row['기존암진단비']),
                                float(row['기존뇌진단비'])
                            ))
                        
                        conn.commit()
                        conn.close()
                        
                        st.success(f"✅ {len(df)}명 고객 정보 저장 완료!")
                        st.rerun()
                
                except Exception as e:
                    st.error(f"❌ 오류: {str(e)}")
        
        # 탭 2: 상담 기록
        with tab2:
            st.markdown("**상담 내용 기록**")
            
            conn = sqlite3.connect(DB_PATH)
            customers_df = pd.read_sql_query("SELECT DISTINCT customer_id, name FROM customers", conn)
            conn.close()
            
            if not customers_df.empty:
                selected_customer = st.selectbox(
                    "고객 선택",
                    options=customers_df["customer_id"].tolist(),
                    format_func=lambda x: f"{x} - {customers_df[customers_df['customer_id']==x]['name'].values[0]}"
                )
                
                note_type = st.selectbox("상담 유형", ["STT 요약", "전화 통화", "방문 상담", "기타"])
                note_content = st.text_area("상담 내용", height=100)
                
                if st.button("💾 저장", use_container_width=True):
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("""
                    INSERT INTO consultation_notes (customer_id, note_type, content)
                    VALUES (?, ?, ?)
                    """, (selected_customer, note_type, note_content))
                    conn.commit()
                    conn.close()
                    st.success("✅ 저장 완료!")
        
        # 탭 3: 고객 현황
        with tab3:
            st.markdown("**전체 고객 정보**")
            
            conn = sqlite3.connect(DB_PATH)
            customers_df = pd.read_sql_query("SELECT * FROM customers", conn)
            conn.close()
            
            if not customers_df.empty:
                st.dataframe(customers_df, use_container_width=True)
                st.write(f"**총 고객 수: {len(customers_df)}명**")
            else:
                st.info("아직 고객 정보가 없습니다.")
    
    # ====================================================================
    # 【우측】 업셀링 감지 & 카톡 발송
    # ====================================================================
    
    with right_col:
        st.markdown("### 🚨 업셀링 감지 & 카톡 발송")
        
        # 출장 정보 입력
        st.markdown("**출장 정보 설정**")
        travel_date = st.date_input("출장 날짜", value=datetime.now())
        travel_region = st.selectbox("출장 지역", ["서울/경기", "부산/영남", "대전/충청", "광주/전라", "대구/경북"])
        
        if st.button("🔍 업셀링 대상 검색", use_container_width=True):
            conn = sqlite3.connect(DB_PATH)
            customers_df = pd.read_sql_query("SELECT * FROM customers", conn)
            conn.close()
            
            if customers_df.empty:
                st.warning("⚠️ 고객 데이터를 먼저 업로드해주세요.")
            else:
                # 업셀링 대상 (암보장 5000만 미만)
                upsell_targets = customers_df[customers_df['cancer_coverage'] < 5000]
                
                if not upsell_targets.empty:
                    st.markdown(f"### 🚨 업셀링 대상자 ({len(upsell_targets)}명)")
                    
                    for _, row in upsell_targets.iterrows():
                        c_id = row['customer_id']
                        c_name = row['name']
                        c_cancer = row['cancer_coverage']
                        c_stroke = row['brain_coverage']
                        c_phone = row['phone']
                        c_address = row['address']
                        
                        # 비즈니스 로직: 맞춤 메시지 생성
                        msg = f"""[{c_name} 고객님 기존 보장 상향 안내]

안녕하세요, 담당 설계사입니다.

📊 가입 분석 결과:
- 최신 업계 표준: 최소 5,000만 원 보장 권장
- 근거: 금융감독원 및 보험협회 최신 공시 개정 표준
- ❌ 고객님 기존: 암 {int(c_cancer):,}만 / 뇌 {int(c_stroke):,}만

{travel_date.strftime('%m월 %d일')}에 {travel_region} 출장 가는 길에 상향 설계안을 전해드리겠습니다.

🔗 예약 링크: https://pro-pipe.app/reserve?id={c_id}"""
                        
                        # 카톡 링크 생성
                        encoded_msg = quote(msg)
                        kakao_url = f"kakaolink://send?formatted_text={encoded_msg}"
                        
                        # UI 표시
                        st.markdown(f"""
                        <div class="customer-card">
                            <b>{c_name}</b> (ID: {c_id}) - 🚨 업셀링 대상<br>
                            <small>📞 {c_phone} | 📍 {c_address}</small><br>
                            <small>암: {int(c_cancer):,}만원 / 뇌: {int(c_stroke):,}만원</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 카톡 발송 버튼
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f'<a href="{kakao_url}" target="_blank" style="background:#FFE812; color:#000; padding:8px 16px; border-radius:6px; text-decoration:none; font-weight:bold; display:inline-block; width:100%; text-align:center;">💬 카톡 발송</a>', unsafe_allow_html=True)
                        
                        with col2:
                            if st.button(f"📋 복사", key=f"copy_{c_id}", use_container_width=True):
                                st.code(msg)
                
                else:
                    st.info("✅ 모든 고객이 기준을 충족합니다.")
        
        # 지역별 필터링
        st.markdown("---")
        st.markdown("### ✈️ 지역별 고객 필터링")
        
        conn = sqlite3.connect(DB_PATH)
        customers_df = pd.read_sql_query("SELECT * FROM customers", conn)
        conn.close()
        
        if not customers_df.empty:
            regions = customers_df["region"].dropna().unique().tolist()
            
            if regions:
                selected_region = st.selectbox("출장 지역 선택", options=regions, key="region_filter")
                
                if st.button("🗺️ 필터링", use_container_width=True):
                    filtered_df = customers_df[customers_df['region'] == selected_region]
                    
                    if not filtered_df.empty:
                        st.success(f"✅ {selected_region}권역 고객 {len(filtered_df)}명")
                        st.dataframe(filtered_df[["customer_id", "name", "phone", "address"]], use_container_width=True)
                    else:
                        st.warning(f"⚠️ {selected_region}권역의 고객이 없습니다.")
    
    # 하단 정보
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #a0aec0; font-size: 12px;">
    🛡️ 보험 파이프라인 CRM v2.0 | Streamlit Cloud
    </div>
    """, unsafe_allow_html=True)
