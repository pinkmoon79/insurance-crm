# 오른쪽 화면에 고객 정보 카드와 AI 타임라인을 그리고 카톡 버튼을 생성하는 파트입니다.
st.markdown(f"""
    <div class="cust-row">
        <span style="font-size:17px; font-weight:700; color:#FFF;">{c_name}</span> &nbsp;<span class="badge-id">{c_id}</span> &nbsp;{badge_style}<br>
        <small style="color:#9CA3AF;">📍 동선 주소: {c_detail} | 📱 {c_phone}</small><br>
        <small style="color:#38BDF8;">📉 기존 가입 보장: 암 {c_cancer}만원 / 뇌 {c_stroke}만원</small>
""", unsafe_allow_html=True)

# 상담 타임라인 출력
cursor.execute("SELECT note_type, content, date FROM ai_notes WHERE customer_id = ? ORDER BY id DESC", (c_id,))
notes = cursor.fetchall()
for n_type, n_content, n_date in notes:
    st.markdown(f"""
        <div class="timeline-box">
            <small style="color:#10B981; font-weight:bold;">{n_type}</small> <small style="color:#9CA3AF;">({n_date})</small><br>
            <span style="font-size:13px; color:#E5E7EB;">{n_content}</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True) # 카드 레이아웃 닫기

# 정밀한 상향 유도 카카오톡 멘트 세팅 및 인코딩
src_fact = "금융감독원 및 보험협회 최신 공시 개정 표준 반영"
if "업셀링" in c_status:
    msg = f"[{c_name} 고객님 기존 보장 상향 안내]\n\n안녕하세요, 담당 설계사입니다. 전산 분석 결과에 따라 안내 드립니다.\n\n📊 가입 분석 결과:\n- 최신 업계 표준: 최소 5,000만 원 보장 권장\n- 근거 데이터: {src_fact}\n- ❌ 고객님 기존 금액: 암 {c_cancer}만 / 뇌 {c_stroke}만 (보장 공백 발생)\n\n제가 {travel_date}에 {c_wide} 출장 가는 길에 상향 보완된 맞춤 설계안을 전해드리고자 합니다. 아래 링크에서 편하신 미팅 시간을 확정해 주세요!\n🔗 링크: https://pro-pipe.app{c_id}"
else:
    msg = f"[{c_name} 고객님 안부 인사]\n\n안녕하세요, 담당 설계사입니다. {travel_date}에 {c_wide} 출장이 있어 연락드렸습니다. 현재 보장 상태는 안정적이나 정기 점검차 잠시 뵙고자 합니다. 아래 링크에서 시간을 골라주세요!\n🔗 링크: https://pro-pipe.app{c_id}"

# 카카오톡 연동 주소 조립 및 노란색 전송 버튼 생성
encoded_msg = urllib.parse.quote(msg)
share_url = f"https://kakao.com{encoded_msg}"
st.markdown(f'<a href="{share_url}" target="_blank" class="kakaotalk-btn-style">💬 {c_name} 고객에게 상향 권유 카톡 쏘기</a>', unsafe_allow_html=True)
st.write("")
