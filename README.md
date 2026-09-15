# 🛡️ 보험 파이프라인 CRM 시스템

## 개요
보험 설계사의 고객 관리 및 영업 생산성 극대화를 위한 클라우드 기반 CRM 시스템입니다.

## 주요 기능

### ① 데이터 관리
- 엑셀/CSV 파일 대량 업로드
- 고객번호 기준 자동 병합
- 동명이인 완벽 격리

### ② 업셀링 감지
- 자동 임계값 비교
- 빅빅보험 업계 표준 기준 적용
- 실시간 대상자 검출

### ③ 스마트 카톡 발송
- 비즈니스 로직 기반 맞춤 메시지
- 고객 ID 자동 포함
- 한 클릭 카톡 전송

### ④ 상담 타임라인
- STT 요약본 저장
- 고객별 상담 이력 관리

### ⑤ 지역별 필터링
- 출장 지역별 고객 분류
- 동선 최적화

## 기술 스택

- **Frontend**: Streamlit
- **Database**: SQLite
- **Backend**: Python
- **Deployment**: Streamlit Cloud

## 설치 및 실행

### 로컬 환경

```bash
# 1. 저장소 복제
git clone https://github.com/yourusername/insurance-crm.git
cd insurance-crm

# 2. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 앱 실행
streamlit run app.py
```

### Streamlit Cloud 배포

1. GitHub에 저장소 Push
2. https://share.streamlit.io 접속
3. "New app" → GitHub 저장소 선택
4. Branch: main, File: app.py 설정
5. Deploy 클릭

## 보안 설정

### Streamlit Cloud의 Secrets 설정

1. 앱 우측 상단 "Manage app" 클릭
2. "Secrets" 탭에 다음 추가:

```toml
master_id = "master"
master_password = "pipe7979!"
```

### 로컬 테스트용 secrets.toml

`.streamlit/secrets.toml` 파일을 생성:

```toml
master_id = "master"
master_password = "pipe7979!"
```

**주의**: `.gitignore`에 이미 포함되어 있음 (GitHub에 올라가지 않음)

## 사용법

### 1️⃣ 로그인
```
ID: master
Password: pipe7979!
```

### 2️⃣ 고객 데이터 업로드
- 좌측 "엑셀 업로드" 탭
- 필수 컬럼: 고객번호, 이름, 연락처, 거주권역, 상세주소, 기존암진단비, 기존뇌진단비

### 3️⃣ 업셀링 대상 검색
- 출장 날짜 & 지역 설정
- "업셀링 대상 검색" 클릭
- 자동 생성된 맞춤 메시지 확인
- "💬 카톡 발송" 버튼으로 즉시 전송

### 4️⃣ 상담 기록
- "상담 기록" 탭에서 고객별 상담 내용 저장

## API 연동 (향후)

현재는 **Deep Link 방식**(비용 0원)으로 구현:
- PC: 메시지 복사 후 수동 발송
- 모바일: 카톡앱 자동 실행

**향후 카카오 비즈니스 API 도입 예정** (완전 자동발송)

## 문제 해결

### ❌ NameError 발생
- `requirements.txt`의 라이브러리 버전 확인
- `streamlit cache clear` 실행
- Streamlit Cloud에서 앱 재시작

### ❌ 로그인 실패
- Streamlit Cloud의 "Secrets" 설정 확인
- 로컬 `.streamlit/secrets.toml` 생성 여부 확인

### ❌ 데이터베이스 오류
- SQLite DB 파일 삭제 후 재시작
- 엑셀 파일의 필수 컬럼 확인

## 개발자

- **초기 개발**: Claude (AI Assistant)
- **원본 기획**: 핑미 (보험 설계사)

## 라이선스

MIT License

## 피드백 & 개선사항

개선사항이나 버그 리포트는 Issues에 등록해주세요!

---

**⚠️ 중요**: 이 앱은 테스트 목적의 개인 용도입니다. 실제 고객 정보는 주의해서 다루세요!
