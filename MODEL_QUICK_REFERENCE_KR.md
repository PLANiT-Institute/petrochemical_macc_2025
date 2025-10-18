# 석유화학 MACC 모델 - 빠른 참조 가이드

**버전:** 2.0 | **업데이트:** 2025-10-18

---

## 🎯 모델 한눈에 보기

```
248개 시설 → 51.4 MtCO₂ → 4개 기술 → 2030년 최대 51.3 MtCO₂ 감축 (98.6%)
```

---

## 📊 핵심 결과 (2030년)

| 기술 | 감축량 | MACC | 순위 | 적용 대상 |
|------|--------|------|------|-----------|
| **RE PPA** | 7.7 Mt | **$319/tCO₂** | 1위 | 모든 시설 |
| **NCC-전기** | 20.5 Mt | **$368/tCO₂** | 2위 | NCC 41개 |
| **Heat Pump** | 0.7 Mt | $774/tCO₂ | 3위 | BTX 47개 |
| **NCC-수소** | 22.4 Mt | $1,184/tCO₂ | 4위 | NCC 41개 |

---

## 🔑 핵심 가정 (문헌 기반)

### 에너지 원단위
- **납사 연료**: 29 GJ/ton (이전 105 → 문헌값)
- **납사 배출계수**: 0.0542 tCO₂/GJ (52 Mt 유지 역산)
- **NCC 전력**: 3.0 MWh/ton (RSC 2025, Linde)
- **NCC 수소**: 0.18 ton/ton (문헌 조사)

### 기술 비용
| 기술 | CAPEX 2025 | OPEX | 출처 |
|------|------------|------|------|
| Heat Pump | $900 M/Mt | 3% | $800-900/kW_th |
| NCC-H₂ | $1,725 M/Mt | 4% | $2,800-3,000/ton |
| NCC-전기 | $1,840 M/Mt | 3.5% | $3,000-3,500/ton |

### 가격 전망
```
H₂:  $12/kg (2025) → $2/kg (2050)      [IEA]
RE:  $130/MWh (2025) → $55/MWh (2050)  [IRENA + 한국 PPA]
Grid: $100/MWh (고정)
```

---

## 🧮 계산 공식

### MACC 기본식
```
MACC = (CAPEX/수명 + OPEX + 연료비) / 감축량

핵심 변경사항:
✅ 할인율 제거 (CAPEX / 수명)
✅ 화석연료 절감 제외 (신규 에너지 비용만)
✅ 모든 전기 = 재생에너지 (0.05 tCO₂/MWh)
```

### 예시: NCC-전기 (2030)

```python
# Baseline 배출
baseline = 29.0 GJ/ton × 0.0542 tCO₂/GJ = 1.739 tCO₂/ton

# 전환 후 배출 (재생에너지!)
elec_emissions = 3.0 MWh/ton × 0.05 tCO₂/MWh = 0.15 tCO₂/ton

# 감축량
abatement = 1.739 - 0.15 = 1.59 tCO₂/ton

# 비용
CAPEX_ann = 1,560 / 25 = 62.4 $/tCO₂
OPEX = 1,560 × 0.035 = 54.6 $/tCO₂
전력비 = 3.0 × 118.8 / 1.59 = 224 $/tCO₂

# MACC
MACC = 62.4 + 54.6 + 224 = 341 $/tCO₂
```

---

## 🔄 데이터 흐름

```
Excel 가정값
  ↓
CSV 변환
  ↓
Module 1 → 248개 시설 배출량 계산
  ↓
Module 2 → MACC 계산 (4개 기술 × 26년)
  ↓
Module 3 → 비용 최적화 (LP)
  ↓
Module 4 → NPV/IRR 계산
```

---

## ⚡ 빠른 실행

```bash
# 전체 실행
python run_all.py

# 개별 모듈
python run_module_02.py  # MACC만

# 결과 확인
ls outputs/module_02/
```

---

## 📁 주요 파일

### 입력
- `data/MACC_Model_Assumptions_v2_Korean.xlsx` - 마스터 가정값
- `data/baseline_2025_detailed.csv` - 248개 시설
- `data/technology_parameters.csv` - 기술 파라미터

### 출력
- `output/macc_results_final.csv` - MACC 전체 결과
- `outputs/module_03/conservative_deployment.csv` - 시나리오별 배포

---

## 🎨 시각화

### 생성되는 그래프
1. **MACC Curve** (2030, 2050)
2. **Cost Evolution** (2025-2050)
3. **Deployment Scenarios** (3가지)
4. **Baseline by Product** (248 시설)

---

## ⚠️ 주의사항

### 재생에너지 가정의 중요성

```
Grid 전력 사용 시:
  NCC-전기 감축량 = 1.739 - 1.35 = 0.39 tCO₂/ton  ❌

RE 전력 사용 시:
  NCC-전기 감축량 = 1.739 - 0.15 = 1.59 tCO₂/ton  ✅ (4배!)
```

### NCC-H₂ vs NCC-전기

```
2030: NCC-전기 우세 ($368 < $1,184)
2050: NCC-수소 우세 ($332 < $195)

전략: 2030년대 전기화 → 2040년대 수소 전환
```

---

## 📚 문헌 출처

| 항목 | 출처 |
|------|------|
| NCC CAPEX | 산업 보고서 ($2,800-3,500/ton) |
| NCC 전력 | RSC Green Chemistry 2025 (Woo et al.) |
| H₂ 가격 | IEA Hydrogen Strategy (2021) |
| RE 가격 | IRENA + 한국 PPA 입찰 데이터 |
| 배출계수 | IEA, IPCC AR6 |

---

## 🔍 문제 해결

### 결과가 이상하다면?

1. **Naphtha fuel 확인**: 29 GJ/ton인지 확인
2. **Naphtha EF 확인**: 0.0542 tCO₂/GJ인지 확인
3. **RE 가정 확인**: 전기 기술이 0.05 tCO₂/MWh 사용하는지 확인
4. **Total 확인**: 51.4 MtCO₂ baseline 유지되는지 확인

### MACC 값이 음수?

- RE PPA 가격이 grid보다 낮으면 음수 MACC 가능
- 현재 설정: RE $130 > Grid $100 (2025)

---

## 📞 연락처

- **모델 문의**: [이메일]
- **상세 문서**: `MODEL_STRUCTURE_KR.md` (41페이지 전체 설명)
- **영문 논문**: `latex_paper/main.tex`

---

**최종 업데이트:** 2025-10-18
**버전:** 2.0 (문헌 기반, 단순 연간화)
