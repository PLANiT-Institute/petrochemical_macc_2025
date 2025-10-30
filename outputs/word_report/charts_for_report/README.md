# 보고서용 차트 파일 안내

## 📊 생성된 차트 목록 (총 6개)

### 1. 01_scenario_cost_comparison.png (165 KB)
**제목**: 6개 시나리오 비용 비교 (2025-2050 누적)
**유형**: 막대그래프
**사용 위치**: Word 보고서 3장 "시나리오별 상세 결과"
**설명**: 
- 6개 시나리오의 2050년 누적 비용을 비교
- 청록색: NCC-H₂ 경로
- 노란색: NCC-전기 경로
- 각 막대 위에 비용 값 표시

---

### 2. 02_company_abatement_top10.png (138 KB)
**제목**: 기업별 감축 잠재량 Top 10
**유형**: 수평 막대그래프
**사용 위치**: Word 보고서 4장 "기업별 전환 분석"
**설명**:
- Top 10 배출 기업의 감축 잠재량
- 색상 그라데이션으로 강조
- 1위: LG Chem (11.4 Mt)
- 2위: Yeochon NCC (9.5 Mt)
- 3위: Lotte Chemical (9.3 Mt)

---

### 3. 03_company_tech_mix_top10.png (158 KB)
**제목**: 기업별 기술 믹스 (Top 10)
**유형**: 누적 막대그래프
**사용 위치**: Word 보고서 4장 "기업별 전환 분석"
**설명**:
- Top 10 기업의 기술별 적용 비율
- 빨강: Heat Pump
- 청록: NCC-H₂
- 연두: NCC-전기
- 노랑: RE_PPA

---

### 4. 04_regional_abatement.png (118 KB)
**제목**: 지역별 감축 잠재량
**유형**: 막대그래프
**사용 위치**: Word 보고서 5장 "지역별 전환 분석"
**설명**:
- 4대 클러스터의 감축 잠재량
- 여수: 26.4 Mt (39.9%)
- 대산: 22.4 Mt (33.8%)
- 울산: 10.4 Mt (15.7%)
- 온산: 6.6 Mt (10.0%)

---

### 5. 05_regional_share_donut.png (315 KB)
**제목**: 지역별 감축 잠재량 분포
**유형**: 도넛 차트
**사용 위치**: Word 보고서 5장 "지역별 전환 분석"
**설명**:
- 각 지역의 상대적 비중을 원형으로 표시
- 여수와 대산이 전체의 73.7% 차지
- 범례에 각 지역의 절대값 표시

---

### 6. 06_regional_tech_mix.png (85 KB)
**제목**: 지역별 기술 믹스
**유형**: 누적 막대그래프
**사용 위치**: Word 보고서 5장 "지역별 전환 분석"
**설명**:
- 4개 지역의 기술별 적용 비율
- 지역별 기술 전략 차이 시각화

---

## 🔧 Word 문서에 삽입 방법

### 1단계: Word 문서 열기
파일: `MACC_Model_Detailed_Report_20251030.docx`

### 2단계: 플레이스홀더 찾기
Ctrl+F (맥: Cmd+F)로 "[그림 위치:" 검색

### 3단계: 차트 삽입
1. 플레이스홀더 위치 확인
2. 해당 PNG 파일 삽입
3. "(여기에 캡처한 그림 삽입)" 텍스트 삭제
4. 그림 크기 조정 (페이지 너비 80-90%)

### 4단계: 그림 제목 추가 (선택사항)
- 삽입 > 캡션
- "그림 1", "그림 2" 등 번호 자동 지정
- 위치: 그림 아래

---

## ⚠️ 한글 폰트 문제

**현상**: PNG 파일 내 한글 텍스트가 깨져 보일 수 있음
**원인**: macOS matplotlib에서 한글 폰트 미지원
**해결 방법**:
1. **옵션 A**: 그대로 사용 (데이터는 정확함)
2. **옵션 B**: 이미지 편집 도구에서 한글 텍스트 수정
3. **옵션 C**: Streamlit Cloud에서 직접 캡처 사용

## 📊 Streamlit Cloud에서 캡처 (권장)

한글이 완벽하게 표시되는 차트를 원한다면:

1. **Streamlit 앱 접속**: https://petrochemical-macc-2025.streamlit.app/
2. **해당 페이지 이동**:
   - 📈 Scenario Comparison → Chart 1
   - 🏢 Company Transition Outlook → Chart 2, 3
   - 🌏 Regional Transition Outlook → Chart 4, 5, 6
3. **스크린샷 캡처**:
   - Windows: Win+Shift+S
   - macOS: Cmd+Shift+4
   - Linux: Shift+PrtSc
4. **Word에 붙여넣기**

---

## 📏 권장 그림 크기

| 차트 | 권장 너비 | 권장 높이 |
|------|----------|----------|
| 01_scenario_cost_comparison.png | 15cm | 7cm |
| 02_company_abatement_top10.png | 14cm | 10cm |
| 03_company_tech_mix_top10.png | 15cm | 7cm |
| 04_regional_abatement.png | 13cm | 7cm |
| 05_regional_share_donut.png | 14cm | 10cm |
| 06_regional_tech_mix.png | 13cm | 7cm |

---

## ✅ 최종 점검

보고서 완성 전 확인사항:

- [ ] 6개 차트 모두 삽입
- [ ] 그림 제목 및 번호 일치
- [ ] 그림 크기 및 위치 적절
- [ ] 한글 텍스트 정상 표시 (또는 Streamlit 캡처로 대체)
- [ ] 페이지 레이아웃 확인
- [ ] PDF 변환 시 그림 품질 확인

---

**생성일**: 2025-10-30
**파일 위치**: `outputs/word_report/charts_for_report/`
**총 파일 크기**: 약 980 KB
**해상도**: 300 DPI (인쇄 품질)
