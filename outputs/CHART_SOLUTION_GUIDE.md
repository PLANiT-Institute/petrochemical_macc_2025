# 차트 품질 개선 가이드

## 문제 상황
- ❌ Python matplotlib에서 한글 폰트 미지원
- ❌ PNG 파일에 한글이 깨져서 표시됨
- ❌ 차트 품질이 만족스럽지 않음

---

## ✅ 권장 해결책: Streamlit Cloud에서 직접 캡처

### 왜 Streamlit이 최선인가?
1. **한글 완벽 표시**: Plotly 라이브러리가 한글 폰트 자동 지원
2. **고품질**: 벡터 기반 렌더링으로 깔끔한 그래프
3. **인터랙티브**: 확대/축소, 호버 정보 등 풍부한 기능
4. **즉시 사용 가능**: 이미 배포되어 작동 중

### 단계별 캡처 방법

#### 1. Streamlit 앱 접속
URL: https://petrochemical-macc-2025.streamlit.app/

#### 2. 각 페이지로 이동하여 캡처

**필요한 차트 6개**:

1. **6개 시나리오 비용 비교**
   - 페이지: 📈 Scenario Comparison
   - 섹션: "Cost Comparison" 차트
   - 캡처: 전체 차트 영역

2. **기업별 감축량 Top 10**
   - 페이지: 🏢 Company Transition Outlook
   - 섹션: "Top 10 Companies by Abatement"
   - 캡처: 막대그래프

3. **기업별 기술 믹스**
   - 페이지: 🏢 Company Transition Outlook
   - 섹션: "Technology Mix by Company"
   - 캡처: 누적 막대그래프

4. **지역별 감축량**
   - 페이지: 🌏 Regional Transition Outlook
   - 섹션: "Total Abatement by Region"
   - 캡처: 막대그래프

5. **지역별 비중 (도넛)**
   - 페이지: 🌏 Regional Transition Outlook
   - 섹션: "Regional Share of Total Abatement"
   - 캡처: 파이차트

6. **지역별 기술 믹스**
   - 페이지: 🌏 Regional Transition Outlook
   - 섹션: "Technology Mix by Region"
   - 캡처: 누적 막대그래프

#### 3. 캡처 도구 사용

**macOS**:
- `Cmd + Shift + 4` → 마우스로 영역 선택
- 또는 `Cmd + Shift + 5` → 스크린샷 옵션

**Windows**:
- `Win + Shift + S` → Snipping Tool
- 영역 선택 모드

**캡처 팁**:
- 차트만 깔끔하게 선택 (여백 최소화)
- 제목과 범례 포함
- 고해상도 모니터에서 캡처 권장

#### 4. Word에 삽입
1. 캡처한 이미지를 Word 문서의 플레이스홀더 위치에 붙여넣기
2. 그림 크기 조정 (페이지 너비 80-90%)
3. 그림 제목 추가 (선택사항)

---

## 📊 추가 요청: 지역별 에너지 전환 흐름도

### 방법 1: PowerPoint로 직접 제작 (권장)

**구조**:
```
[4대 클러스터]
    여수 (39.9%)  →  [기술 적용]  →  [에너지 전환]  →  [2050년 상태]
    대산 (33.8%)  →  Heat Pump      →  LNG → 전기    →  배출 감소
    울산 (15.7%)  →  RE_PPA         →  Grid → RE     →  
    온산 (10.0%)  →  NCC-H₂/전기    →  Fossil → H₂/RE →
```

**PowerPoint 템플릿 제공**:
SmartArt 또는 도형을 사용하여 제작 권장

### 방법 2: Python으로 간단한 흐름도 (영문 버전)

데이터만 제공하고, 레이블은 PowerPoint에서 한글로 수정

---

## 💡 최종 권장사항

### 우선순위 1: Streamlit 캡처 (★★★★★)
- **장점**: 한글 완벽, 고품질, 즉시 사용
- **단점**: 수동 캡처 필요 (하지만 10분이면 완료)
- **추천도**: ⭐⭐⭐⭐⭐

### 우선순위 2: Python PNG 파일 + Word 편집 (★★★☆☆)
- **장점**: 자동화 가능
- **단점**: 한글 깨짐, 추가 편집 필요
- **추천도**: ⭐⭐⭐☆☆

### 우선순위 3: PowerPoint에서 재작성 (★★☆☆☆)
- **장점**: 완전한 커스터마이징
- **단점**: 시간 소요 큼
- **추천도**: ⭐⭐☆☆☆

---

## ⏱️ 소요 시간 비교

| 방법 | 소요 시간 | 품질 | 한글 지원 |
|------|----------|------|----------|
| Streamlit 캡처 | 10분 | ⭐⭐⭐⭐⭐ | ✅ 완벽 |
| Python PNG | 자동 | ⭐⭐⭐☆☆ | ❌ 깨짐 |
| PowerPoint | 30분+ | ⭐⭐⭐⭐⭐ | ✅ 완벽 |

---

## 🎯 즉시 실행 가능한 액션

### 지금 바로 할 수 있는 것:

1. **Streamlit 앱 열기**: https://petrochemical-macc-2025.streamlit.app/
2. **시나리오 선택**: "Shaheen (성장) + NCC-H₂"
3. **각 페이지 방문하여 캡처**:
   - 📈 Scenario Comparison (1개 차트)
   - 🏢 Company Transition Outlook (2개 차트)
   - 🌏 Regional Transition Outlook (3개 차트)
4. **Word 문서에 삽입**
5. **완료!**

**예상 소요 시간**: 10-15분
**결과물 품질**: ⭐⭐⭐⭐⭐

---

## 📧 추가 지원

### 지역별 에너지 전환 흐름도가 필요하다면:

**옵션 A**: Streamlit 앱에 새 페이지 추가
- Sankey diagram으로 에너지 흐름 시각화
- 한글 지원 보장
- 30분 소요

**옵션 B**: PowerPoint 템플릿 제공
- SmartArt 기반 흐름도 템플릿
- 데이터 표 제공
- 직접 편집 가능

어떤 옵션을 원하시나요?

---

**결론**: Streamlit Cloud에서 캡처하는 것이 가장 빠르고 품질도 최고입니다!
