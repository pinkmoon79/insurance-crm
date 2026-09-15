import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from urllib.parse import quote
from PIL import Image
import io

st.set_page_config(page_title="보험 CRM", page_icon="🛡️", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🛡️ 로그인")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        u = st.text_input("ID")
        p = st.text_input("PW", type="password")
        if st.button("로그인"):
            if u == st.secrets.get("master_id", "master") and p == st.secrets.get("master_password", "pipe7979!"):
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("오류")
else:
    if st.sidebar.button("로그아웃"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.title("🛡️ 보험 CRM")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 대시보드", "👥 고객", "🚨 업셀링", "📋 정책", "🤖 AI분석"])
    
    with tab1:
        st.header("대시보드")
        try:
            conn = sqlite3.connect("insurance_crm.db")
            cust = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0] if conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='customers'").fetchone() else 0
            policy = conn.execute("SELECT COUNT(*) FROM policy_updates WHERE reviewed = 1").fetchone()[0] if conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='policy_updates'").fetchone() else 0
            auto = conn.execute("SELECT COUNT(*) FROM policy_updates WHERE auto_detected = 1 AND reviewed = 0").fetchone()[0] if conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='policy_updates'").fetchone() else 0
            conn.close()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("고객", cust)
            col2.metric("정책", policy)
            col3.metric("🤖대기", auto)
        except:
            st.info("데이터 없음")
    
    with tab2:
        st.header("고객 관리")
        f = st.file_uploader("엑셀/CSV", type=["xlsx", "csv"])
        if f:
            df = pd.read_excel(f) if f.name.endswith('.xlsx') else pd.read_csv(f)
            st.dataframe(df.head())
            if st.button("저장"):
                conn = sqlite3.connect("insurance_crm.db")
                conn.execute("CREATE TABLE IF NOT EXISTS customers (customer_id TEXT PRIMARY KEY, name TEXT, phone TEXT, region TEXT, address TEXT, cancer_coverage REAL, brain_coverage REAL)")
                for _, row in df.iterrows():
                    conn.execute("INSERT OR REPLACE INTO customers VALUES (?,?,?,?,?,?,?)",
                        (str(row['고객번호']).strip(), str(row['이름']).strip(), str(row['연락처']).strip(),
                         str(row['거주권역']).strip(), str(row['상세주소']).strip(), float(row['기존암진단비']), float(row['기존뇌진단비'])))
                conn.commit()
                conn.close()
                st.success(f"{len(df)}명 저장!")
    
    with tab3:
        st.header("업셀링")
        d = st.date_input("날짜")
        r = st.selectbox("지역", ["서울/경기", "부산/영남", "대전/충청", "광주/전라", "대구/경북"])
        if st.button("검색"):
            conn = sqlite3.connect("insurance_crm.db")
            try:
                c = conn.execute("SELECT customer_id, name, phone, cancer_coverage, brain_coverage FROM customers WHERE cancer_coverage < 5000")
                rows = c.fetchall()
            except:
                rows = []
            conn.close()
            
            if rows:
                st.write(f"**업셀링 대상: {len(rows)}명**")
                for cid, name, phone, cancer, brain in rows[:20]:
                    conn = sqlite3.connect("insurance_crm.db")
                    latest_policy = conn.execute("SELECT policy_name FROM policy_updates WHERE reviewed = 1 ORDER BY start_date DESC LIMIT 1").fetchone()
                    conn.close()
                    
                    policy_info = f"\n📋 정책: {latest_policy[0]}" if latest_policy else ""
                    
                    msg = f"[{name}님]\n암:{cancer:.0f}만 뇌:{brain:.0f}만{policy_info}\n{d.strftime('%m월 %d일')} {r}\nhttps://pro-pipe.app/reserve?id={cid}"
                    col1, col2 = st.columns([2, 2])
                    col1.write(f"**{name}** (암: {cancer:.0f}만)")
                    if col2.button("💬", key=cid):
                        st.code(msg)
            else:
                st.info("대상 없음")
    
    with tab4:
        st.header("정책 관리")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("정책명")
        with col2:
            if st.button("등록"):
                if name:
                    conn = sqlite3.connect("insurance_crm.db")
                    conn.execute("CREATE TABLE IF NOT EXISTS policy_updates (id INTEGER PRIMARY KEY, policy_name TEXT, policy_description TEXT, start_date DATE, ai_confidence REAL, status TEXT, auto_detected BOOLEAN, reviewed BOOLEAN DEFAULT 0)")
                    conn.execute("INSERT INTO policy_updates (policy_name, policy_description, start_date, ai_confidence, status, auto_detected) VALUES (?,?,?,?,?,?)",
                        (name, name, datetime.now().date(), 0.5, "대기", 0))
                    conn.commit()
                    conn.close()
                    st.success("등록!")
                    st.rerun()
        
        st.subheader("검토 대기")
        conn = sqlite3.connect("insurance_crm.db")
        try:
            rows = conn.execute("SELECT id, policy_name, auto_detected FROM policy_updates WHERE reviewed = 0").fetchall()
            if rows:
                for pid, pname, auto in rows:
                    badge = "🤖" if auto else "👤"
                    col1, col2, col3 = st.columns([3, 1, 1])
                    col1.write(f"{badge} {pname}")
                    if col2.button("✅", key=f"a{pid}", use_container_width=True):
                        conn.execute("UPDATE policy_updates SET reviewed = 1 WHERE id = ?", (pid,))
                        conn.commit()
                        st.rerun()
                    if col3.button("❌", key=f"r{pid}", use_container_width=True):
                        conn.execute("UPDATE policy_updates SET reviewed = 1, status = '거절' WHERE id = ?", (pid,))
                        conn.commit()
                        st.rerun()
            else:
                st.info("정책 없음")
        except:
            st.info("정책 없음")
        finally:
            conn.close()
    
    with tab5:
        st.header("🤖 AI 정책 분석")
        
        subtab1, subtab2 = st.tabs(["📝 텍스트", "📸 이미지 OCR"])
        
        with subtab1:
            st.write("**뉴스/공지사항 텍스트를 붙여넣으면 AI가 정책을 자동 추출합니다**")
            
            text_input = st.text_area("텍스트 붙여넣기", placeholder="뉴스나 공지사항 텍스트...", height=150, key="text_input")
            
            if st.button("🔍 AI로 정책 추출", use_container_width=True, key="text_analyze"):
                if not text_input.strip():
                    st.warning("⚠️ 텍스트를 입력하세요")
                else:
                    analyze_text(text_input)
        
        with subtab2:
            st.write("**카톡 스크린샷이나 뉴스 이미지를 업로드하면 OCR로 텍스트를 추출합니다**")
            
            img_file = st.file_uploader("이미지 업로드 (JPG, PNG)", type=["jpg", "jpeg", "png"])
            
            if img_file:
                image = Image.open(img_file)
                st.image(image, caption="업로드된 이미지")
                
                if st.button("🔍 이미지에서 텍스트 추출", use_container_width=True, key="img_analyze"):
                    with st.spinner("📖 이미지 분석 중..."):
                        try:
                            # pytesseract로 OCR 시도
                            import pytesseract
                            extracted_text = pytesseract.image_to_string(image, lang='kor')
                            
                            if extracted_text.strip():
                                st.success("✅ 텍스트 추출 완료!")
                                st.text_area("추출된 텍스트", extracted_text, height=150, disabled=True)
                                
                                if st.button("➡️ 이 텍스트로 분석", use_container_width=True):
                                    analyze_text(extracted_text)
                            else:
                                st.warning("⚠️ 이미지에서 텍스트를 찾을 수 없습니다")
                        
                        except ImportError:
                            st.error("⚠️ Tesseract OCR이 설치되지 않았습니다")
                            st.info("💡 대신 이미지의 텍스트를 수동으로 복사해서 '📝 텍스트' 탭에서 분석하세요")
                        except Exception as e:
                            st.error(f"❌ 오류: {str(e)}")
                            st.info("💡 이미지의 텍스트를 수동으로 복사해서 '📝 텍스트' 탭에서 분석하세요")

def analyze_text(text_input):
    """텍스트에서 정책 추출 함수"""
    keywords = {
        "5세대": ("5세대 실손보험", 0.85),
        "실손": ("실손의료보험", 0.80),
        "암진단": ("암진단비", 0.85),
        "암보": ("암보장", 0.85),
        "특약": ("특약", 0.70),
        "갱신": ("계약갱신", 0.70),
        "금감원": ("금감원 정책", 0.75),
        "보험협회": ("보험협회 공시", 0.75),
        "의료보험": ("의료보험", 0.75),
        "진단비": ("진단비 기준", 0.75),
        "할인": ("보험료 할인", 0.70),
        "보장": ("보장 강화", 0.60),
        "보험료": ("보험료", 0.60),
    }
    
    conn = sqlite3.connect("insurance_crm.db")
    conn.execute("CREATE TABLE IF NOT EXISTS policy_updates (id INTEGER PRIMARY KEY, policy_name TEXT, policy_description TEXT, start_date DATE, ai_confidence REAL, status TEXT, auto_detected BOOLEAN, reviewed BOOLEAN DEFAULT 0)")
    
    detected = []
    text_lower = text_input.lower()
    
    for keyword, (policy_name, conf) in keywords.items():
        if keyword in text_lower:
            check = conn.execute("SELECT id FROM policy_updates WHERE policy_name = ?", (policy_name,)).fetchone()
            if not check:
                conn.execute("INSERT INTO policy_updates (policy_name, policy_description, start_date, ai_confidence, status, auto_detected) VALUES (?,?,?,?,?,?)",
                    (policy_name, text_input[:200], datetime.now().date(), conf, "대기", 1))
                detected.append((policy_name, conf))
    
    conn.commit()
    conn.close()
    
    if detected:
        st.success(f"✅ {len(detected)}개 정책 추출!")
        for pname, conf in detected:
            st.write(f"- **{pname}** (신뢰도: {conf*100:.0f}%)")
        st.info("📌 탭4에서 [✅]를 눌러 승인하세요!")
    else:
        st.info("💡 관련 정책이 없습니다")

st.markdown("---\n<div style='text-align:center;font-size:11px;color:#888;'>🛡️ 보험 파이프라인 CRM</div>", unsafe_allow_html=True)
