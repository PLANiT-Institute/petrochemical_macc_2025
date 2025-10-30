# 전력 모델 전면 수정 완료 보고서
# Electricity Model Complete Overhaul - Summary Report

**날짜 / Date:** 2025-10-30
**상태 / Status:** ✅ 완료 / Completed

---

## 📋 수정 개요 / Overview

사용자 요청에 따라 전력 모델을 처음부터 완전히 재검토하고 수정했습니다.

### 주요 변경사항 / Key Changes

1. **전력 체계 명확화**: 계통 전력 (Grid) vs 재생에너지 (Renewable)
2. **Grid 전력 가격**: 한국 산업용 전력 요금 반영 ($80-100/MWh)
3. **Grid 배출계수**: 현실적 감소 경로 (0.436 → 0.070 tCO₂/MWh, NOT 0)
4. **RE 전력 가격**: Excel assumption 데이터 반영 ($129-191/MWh)
5. **기술 정의 수정**: NCC-Electricity는 Grid 전력 사용 (이전: RE로 잘못 설정)

---

## 🔧 수정된 파일 / Modified Files

### 1. 데이터 파일 / Data Files

#### `data/grid_price_trajectory.csv` (새로 생성 / CREATED)
```
2025: $80/MWh  → 2030: $90/MWh  → 2050: $100/MWh
```
- 출처: 한국전력거래소 산업용 전력 요금
- 특징: 상대적으로 안정적, 소폭 상승

#### `data/grid_emission_trajectory.csv` (수정 / MODIFIED)
```
2025: 0.436 tCO₂/MWh (현재 계통 평균)
2030: 0.350 tCO₂/MWh (10차 전력수급계획 목표)
2040: 0.200 tCO₂/MWh
2050: 0.070 tCO₂/MWh (Net-Zero 목표, 완전 탈탄소는 불가능)
```
- **중요**: 2050년에도 0이 아닌 0.070으로 설정 (계통 안정성 유지 필요)

#### `data/re_price_trajectory.csv` (이미 업데이트됨 / ALREADY UPDATED)
```
2025: $129.29/MWh → 2030: $157.30/MWh → 2050: $191.38/MWh
```
- 출처: Excel assumption 데이터
- 특징: Grid 대비 60-90% 비싸며, 시간에 따라 더 비싸짐

#### `data/technology_parameters.csv` (notes 업데이트 / NOTES UPDATED)
- NCC-Electricity: "Electric cracking using **GRID electricity** | 5.5 MWh/ton"
- Heat_Pump: "Heat pump for <165C processes using **GRID electricity** | COP=4.0"
- 명확화: 모든 전력 기술은 기본적으로 Grid 전력 사용

### 2. 코드 파일 / Code Files

#### `modules/utils.py` (메서드 추가 / METHOD ADDED)
```python
def load_grid_prices(self):
    """Load grid electricity price trajectory"""
    return pd.read_csv(self.data_dir / 'grid_price_trajectory.csv')
```

#### `modules/macc.py` (대규모 수정 / EXTENSIVELY MODIFIED)

**주요 변경사항:**

1. **Grid prices 로딩 추가**
```python
self.df_grid_prices = loader.load_grid_prices()
```

2. **메인 계산 루프 수정**
```python
# Get GRID electricity price and emission factor
grid_price = self.df_grid_prices[self.df_grid_prices['year'] == year]['grid_price_usd_per_mwh'].iloc[0]
grid_ef = self.df_grid_emission[self.df_grid_emission['year'] == year]['grid_ef_tco2_per_mwh'].iloc[0]

# NCC-Electricity uses GRID electricity
ncc_elec_macc = self._calculate_ncc_electricity_macc(year, grid_price, grid_ef, naphtha_price)
```

3. **`_calculate_ncc_electricity_macc()` 메서드 수정**
   - 매개변수 변경: `re_price, re_ef` → `grid_price, grid_ef`
   - 전력 배출량 계산: `emission_elec_per_ton = elec_mwh_per_ton * grid_ef`
   - 전력 비용 계산: `electricity_cost_per_ton = elec_mwh_per_ton * grid_price`
   - 반환값에 `grid_ef_tco2_per_mwh`, `grid_price_usd_per_mwh` 포함

4. **버그 수정**
   - UnboundLocalError: grid_ef를 사용하기 전에 정의
   - NameError: 반환 딕셔너리에서 `re_ef` → `grid_ef` 변경

---

## ✅ 검증 결과 / Verification Results

### 전력 모델 테스트 / Electricity Model Test

**NCC-Electricity (Grid 전력 사용 확인)**
```
Year 2030: Grid $90/MWh, EF 0.350 tCO₂/MWh → MACC $125/tCO₂
Year 2040: Grid $100/MWh, EF 0.200 tCO₂/MWh → MACC $92/tCO₂
Year 2050: Grid $100/MWh, EF 0.070 tCO₂/MWh → MACC $75/tCO₂
```

**RE_PPA (Grid → RE 전환 비용)**
```
Year 2030: $524/tCO₂ (Grid EF 높음, 전환 효과 큼)
Year 2040: $1,276/tCO₂ (Grid EF 낮아짐, 전환 효과 감소)
Year 2050: $9,569/tCO₂ (Grid EF 매우 낮음, 전환 효과 거의 없음)
```

**결과 해석:**
- NCC-Electricity의 MACC가 시간에 따라 감소하는 이유: Grid가 탈탄소화되면서 감축량이 증가하기 때문
- RE_PPA의 MACC가 시간에 따라 증가하는 이유: Grid EF가 낮아져 전환 효과가 감소하고, RE 가격은 상승하기 때문

### 경고 / 에러 검증 / Warnings/Errors Verification

✅ **divide by zero 경고 없음** - 이전 모델의 주요 문제 해결됨
✅ **모든 계산 정상 실행**
✅ **Grid 관련 컬럼 정상 생성**: `grid_ef_tco2_per_mwh`, `grid_price_usd_per_mwh`

---

## 📊 3개 생산 시나리오 결과 / 3 Production Scenarios Results

### 2050년 결과 비교 / 2050 Results Comparison

| 시나리오 | BAU 배출량 | 실제 배출량 | 누적 비용 | NCC-H₂ | RE PPA | Heat Pump |
|---------|-----------|-----------|---------|--------|--------|-----------|
| **Shaheen (성장)** | 68.0 MtCO₂ | 0.0 MtCO₂ | $58.3B | 60.1 Mt | 4.7 Mt | 3.3 Mt |
| **구조조정 25%** | 40.9 MtCO₂ | 0.0 MtCO₂ | $33.3B | 40.9 Mt | 0.0 Mt | 0.0 Mt |
| **구조조정 40%** | 35.5 MtCO₂ | 0.0 MtCO₂ | $29.0B | 33.6 Mt | 0.0 Mt | 1.9 Mt |

### 주요 인사이트 / Key Insights

1. **생산량 감소 시나리오가 비용 효율적**
   - 구조조정 40%: $29.0B (가장 저렴)
   - 구조조정 25%: $33.3B
   - Shaheen (성장): $58.3B (가장 비싼)

2. **NCC-H₂가 주요 감축 기술**
   - 모든 시나리오에서 NCC-H₂가 가장 큰 역할
   - 이유: H₂ 가격 하락 + Grid 전력보다 저렴한 MACC ($116/tCO₂ vs $125/tCO₂ in 2030)

3. **RE PPA 활용 제한적**
   - Shaheen 시나리오에서만 4.7 Mt 활용
   - 이유: 매우 높은 비용 ($524-9,569/tCO₂)

---

## 🎯 주요 성과 / Key Achievements

### ✅ 완료된 작업 / Completed Tasks

1. ✅ 전력 모델 전면 재검토 및 수정
2. ✅ Grid 전력 가격 데이터 생성 (한국 전력 요금 반영)
3. ✅ Grid 배출계수 현실적 경로 설정 (0 제거)
4. ✅ RE 전력 가격 Excel 데이터 반영
5. ✅ MACC 계산 모듈 수정 (Grid 전력 사용)
6. ✅ 3개 생산 시나리오 실행 완료
7. ✅ 결과 검증 (divide by zero 경고 제거)
8. ✅ Streamlit 대시보드 업데이트

### 📁 생성된 파일 / Generated Files

**데이터 파일:**
- `data/grid_price_trajectory.csv`
- `data/grid_emission_trajectory.csv` (수정)
- `data/technology_parameters.csv` (수정)

**분석 스크립트:**
- `comprehensive_model_review.py` (진단 도구)
- `fix_electricity_model.py` (수정 스크립트)

**결과 파일:**
- `outputs/scenarios_shaheen/` (전체 결과)
- `outputs/scenarios_restructure_25pct/` (전체 결과)
- `outputs/scenarios_restructure_40pct/` (전체 결과)
- `outputs/scenarios_comparison/summary.csv`

**대시보드:**
- `dashboard_scenarios.py` (새로운 시나리오 대시보드)

---

## 🚀 사용 방법 / How to Use

### 1. Streamlit 대시보드 실행 / Run Streamlit Dashboard

```bash
streamlit run dashboard_scenarios.py
```

대시보드 기능:
- 📊 **시나리오 비교**: 3개 시나리오 2050년 결과 비교
- 📈 **MACC 곡선**: 시나리오별, 연도별 MACC 곡선
- 💰 **비용 분석**: 기술별 MACC 및 감축 잠재력 추이
- 🔋 **전력 모델**: Grid vs RE 가격 및 배출계수 비교

### 2. 시나리오 재실행 / Re-run Scenarios

```bash
python run_all_scenarios_v2.py
```

### 3. 결과 확인 / Check Results

```bash
# 시나리오 비교 요약
cat outputs/scenarios_comparison/summary.csv

# 개별 시나리오 MACC 결과
cat outputs/scenarios_shaheen/module_02_macc/macc_annual_2025_2050.csv
```

---

## 📝 다음 단계 / Next Steps

### 권장 사항 / Recommendations

1. **Word 보고서 업데이트**
   - 전력 모델 변경사항 반영
   - 3개 시나리오 결과 포함
   - Grid vs RE 전력 설명 추가

2. **RE_PPA 기술 재검토**
   - 현재: Grid → RE 전환 옵션으로 구현됨
   - 문제: 매우 높은 비용으로 활용도 낮음
   - 선택지:
     - Option A: 유지 (선택적 감축 옵션)
     - Option B: 삭제 (Grid 탈탄소화에만 의존)

3. **추가 시나리오 고려**
   - RE 전력 가격 하락 시나리오
   - NCC-Electricity 활용 시나리오 (현재는 NCC-H₂가 선호됨)

---

## 📞 문의 / Contact

이 보고서는 2025-10-30에 작성되었으며, 전력 모델 전면 수정 작업의 완료를 문서화합니다.

모든 변경사항은 Git으로 버전 관리되고 있습니다.

---

## 🔍 기술적 세부사항 / Technical Details

### 전력 모델 구조 / Electricity Model Structure

```
전력 유형 / Electricity Types:
├── Grid Electricity (계통 전력)
│   ├── 가격: $80-100/MWh
│   ├── 배출계수: 0.436 → 0.070 tCO₂/MWh
│   └── 사용 기술: NCC-Electricity, Heat_Pump
│
└── Renewable Electricity (재생에너지)
    ├── 가격: $129-191/MWh
    ├── 배출계수: 0.0 tCO₂/MWh
    └── 사용 기술: RE_PPA (선택적)
```

### MACC 계산 로직 / MACC Calculation Logic

**NCC-Electricity (전기 분해로):**
```
감축량 = Baseline 연소 배출 - Grid 전력 배출
       = (기존 화석연료 연소) - (Grid EF × 5.5 MWh/ton)

비용 = (CAPEX + OPEX + Grid 전력 비용) / 감축량

Grid EF 감소 → 감축량 증가 → MACC 감소 (시간에 따라)
```

**RE_PPA (재생에너지 전환):**
```
감축량 = Grid 전력 배출 - RE 전력 배출
       = (Grid EF × 전력 소비) - 0

비용 = (RE 가격 - Grid 가격) × 전력량 / 감축량

Grid EF 감소 → 감축량 감소 → MACC 증가 (시간에 따라)
RE 가격 상승 + Grid 가격 안정 → MACC 더욱 증가
```

### 데이터 흐름 / Data Flow

```
Data Files → DataLoader → MACCAnalyzer → Results
     ↓           ↓              ↓            ↓
grid_price → load_grid_  → _calculate_ → macc_annual_
trajectory   prices()       ncc_macc()    2025_2050.csv
```

---

**End of Report / 보고서 끝**
