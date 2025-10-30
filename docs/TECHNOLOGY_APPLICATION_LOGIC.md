# 기술별 적용 논리 정리
**Technology Application Logic: NCC vs Non-NCC Facilities**

**Date**: 2025-10-30
**Purpose**: 각 감축 기술이 어떤 공정에 적용되는지 명확히 정리

---

## 1. 시설 분류

### 1.1 NCC (Naphtha Cracking Complex) 시설

**제품**:
- Ethylene (에틸렌)
- Propylene (프로필렌)
- Butadiene (부타디엔)

**프로세스**: Naphtha Cracker (납사 분해)

**특징**:
- **고온 공정** (~850°C): 납사를 고온에서 크래킹하여 올레핀 생산
- **대량 화석연료 연소**: 40 GJ/ton (전체 배출의 ~70%)
- **한국 석유화학 산업의 핵심**: 11개 시설, 총 배출량 ~30 MtCO2 (2025)

**에너지 구조** (에틸렌 1톤 기준):
```
연소 에너지:        40.2 GJ/ton  (Naphtha 부생가스 + LNG + Fuel Gas)
프로세스 전력:      21.8 kWh/ton (분리, 압축 등)
───────────────────────────────────────────────────────
총 배출량:          2.26 tCO2/ton
  - 연소 (95.7%):   2.16 tCO2/ton
  - 전력 (4.3%):    0.10 tCO2/ton
```

---

### 1.2 Non-NCC 시설

**제품군**:
- **Aromatics (방향족)**: Benzene, Toluene, Xylene
- **Polymers (중합체)**: PE, PP, PS, PVC
- **Intermediates (중간재)**: TPA, EG, Phenol, Acetone
- **Other (기타)**: 다양한 화학제품

**프로세스**: BTX Plant, Polymerization, Synthesis 등

**특징**:
- **중저온 공정** (140-200°C): 대부분 200°C 이하
- **화석연료 연소**: 주로 난방, 증류, 건조 등
- **히트펌프 적용 가능**: 온도가 낮아 전기 히트펌프로 대체 가능

---

## 2. 기술별 적용 대상

### 2.1 NCC-H2 (수소 크래킹)

**적용 대상**: ✅ **NCC 시설만** (Ethylene, Propylene, Butadiene)

**대체 내용**:
```
Before (베이스라인):
  Naphtha → Cracking furnace (850°C)
    - 열원: 부생가스 연소 + LNG + Fuel Gas
    - 배출: 2.26 tCO2/ton ethylene

After (NCC-H2):
  Naphtha → Cracking furnace (850°C)
    - 열원: 수소 연소 (green H2)
    - 배출: 0.0 tCO2/ton ethylene
```

**감축량**: 2.26 tCO2/ton (100%)

**비용** (2030년 기준):
- H2 소비: 0.18 ton/ton (현재) → **0.25-0.30 ton/ton (권장)**
- MACC: $115/tCO2 (현재) → **$400-570/tCO2 (에너지 기반 재계산)**

---

### 2.2 NCC-Electricity (전기 크래킹)

**적용 대상**: ✅ **NCC 시설만** (Ethylene, Propylene, Butadiene)

**대체 내용**:
```
Before (베이스라인):
  Naphtha → Cracking furnace (850°C)
    - 열원: 화석연료 연소 (40 GJ/ton)
    - 배출: 2.26 tCO2/ton ethylene

After (NCC-Electricity):
  Naphtha → Electric cracking furnace (850°C)
    - 열원: 전기 가열 (3.0 MWh/ton = 10.8 GJ/ton)
    - 전력: 재생에너지 (RE)
    - 배출: 0.15 tCO2/ton (RE lifecycle)
```

**감축량**: 2.11 tCO2/ton (93%)

**비용** (2030년 기준):
- 전력 소비: 3.0 MWh/ton (문헌 검증됨)
- MACC: $117/tCO2 (현재) → **$217/tCO2 (에너지 기반)**

**장점**:
- 수소 대비 **2-3배 저렴**
- 기술 성숙도 높음 (BASF eFurnace™ 상업화 진행 중)

---

### 2.3 RE PPA (재생에너지 전력 구매 계약)

**적용 대상**: ✅ **NCC 시설의 프로세스 전력만**

**대체 내용**:
```
Before (베이스라인):
  NCC 프로세스 전력: 21.8 kWh/ton ethylene
    - 전력원: Grid electricity (0.45 tCO2/MWh in 2025)
    - 배출: 0.10 tCO2/ton ethylene

After (RE PPA):
  NCC 프로세스 전력: 21.8 kWh/ton ethylene
    - 전력원: Renewable electricity (RE PPA)
    - 배출: 0.005 tCO2/ton (RE lifecycle)
```

**감축량**: 0.095 tCO2/ton (전력 배출의 95%)

**비용** (2030년 기준):
- CAPEX: $0 (계약 기반)
- OPEX: $0 (RE 가격에 포함)
- MACC: RE 가격에 따라 변동 (2030: $50-100/tCO2)

**특징**:
- **가장 간단한 감축 수단**: 인프라 투자 불필요
- **즉시 실행 가능** (2025년부터)
- **감축 잠재량 작음**: 전력 배출은 총 배출의 4.3%만

**⚠️ 현재 모델 제약**:
- RE PPA는 **NCC 전력만** 대상 (코드 line 408-411)
- 이유: "User specified: RE is only applied to NCC" (주석 line 395)
- **질문**: 왜 Non-NCC 시설의 전력은 RE PPA 대상이 아닌가?
  - → Heat Pump 도입 시 전력 소비가 급증하므로, 자동으로 RE 전력 사용 가정?

---

### 2.4 Heat Pump (전기 히트펌프)

**적용 대상**: ✅ **Non-NCC 시설만** (BTX, Polymers, Intermediates 등)

**제품군별 적용률** (온도 제약):
| 제품군 | 적용률 | 최대 온도 | 비고 |
|--------|--------|----------|------|
| Olefins | 10% | 850°C | 대부분 NCC → Heat Pump 적용 매우 제한적 |
| Aromatics | 60% | 140°C | BTX 분리/정제 → Heat Pump 최적 |
| Polymers | 45% | 180°C | 중합 반응 → Heat Pump 적용 가능 |
| Intermediates | 50% | 150°C | 합성 반응 → Heat Pump 적용 가능 |
| Other | 35% | 200°C | 기타 공정 → 일부 적용 |

**대체 내용**:
```
Before (베이스라인):
  화석연료 연소: X GJ/ton (난방, 증류, 건조 등)
    - 연료: Naphtha, LNG, Fuel Gas, LPG 등
    - 배출: Y tCO2/ton

After (Heat Pump):
  전기 히트펌프: X / COP / 3.6 MWh/ton
    - 전력원: Renewable electricity
    - COP: 4.0 (효율 400%)
    - 배출: RE lifecycle emissions (0.05 tCO2/MWh)
```

**예시 계산**:
```
화석연료 연소: 20 GJ/ton
히트펌프 전력: 20 / 4.0 / 3.6 = 1.39 MWh/ton (75% 에너지 절감!)
배출 감축: 1.08 tCO2/ton → 0.07 tCO2/ton (93% 감축)
```

**비용** (2030년 기준):
- CAPEX: $720 M$/MtCO2
- MACC: ~$100-200/tCO2 (RE 가격에 따라)

**장점**:
- **에너지 효율 극대화**: COP=4.0 → 필요 에너지 75% 감소
- **온도 <200°C 공정에 최적**
- **상업적으로 성숙**: 산업용 히트펌프 기술 확립

**제약**:
- ⚠️ **NCC 시설 제외**: 코드 line 148-152에서 명시적으로 제외
  - 이유: NCC는 고온 (850°C) → 히트펌프 적용 불가
  - NCC는 NCC-H2 또는 NCC-Electricity로 대응

---

## 3. 기술 적용 매트릭스

### 3.1 시설별 적용 가능 기술

| 시설 유형 | NCC-H2 | NCC-Elec | RE PPA | Heat Pump |
|-----------|--------|----------|---------|-----------|
| **NCC (Ethylene, Propylene, Butadiene)** | ✅ | ✅ | ✅ (프로세스 전력) | ❌ (고온) |
| **Aromatics (BTX)** | ❌ | ❌ | ❌ (모델 제약) | ✅ (60%) |
| **Polymers (PE, PP, PS)** | ❌ | ❌ | ❌ (모델 제약) | ✅ (45%) |
| **Intermediates (TPA, EG)** | ❌ | ❌ | ❌ (모델 제약) | ✅ (50%) |
| **Other** | ❌ | ❌ | ❌ (모델 제약) | ✅ (35%) |

### 3.2 배출원별 감축 기술

| 배출원 | 시설 유형 | 감축 기술 |
|--------|-----------|-----------|
| **화석연료 연소 (고온, 850°C)** | NCC | NCC-H2 또는 NCC-Electricity |
| **화석연료 연소 (중저온, <200°C)** | Non-NCC | Heat Pump |
| **프로세스 전력 (그리드)** | NCC | RE PPA |
| **프로세스 전력 (그리드)** | Non-NCC | ❓ (모델에 명시 안 됨) |

---

## 4. 에너지 흐름 다이어그램

### 4.1 NCC 시설 (Ethylene 예시)

#### 베이스라인 (2025)
```
INPUT:
  Naphtha (원료):          105 GJ/ton
  Naphtha (부생가스 연소):  29 GJ/ton  ─┐
  LNG:                      4.5 GJ/ton  ├─ 연소 40.2 GJ/ton
  Fuel Gas:                 5.6 GJ/ton  │  → 2.16 tCO2/ton ❌
  Byproduct Gas:            1.1 GJ/ton ─┘
  Grid Electricity:        21.8 kWh/ton → 0.10 tCO2/ton ❌

OUTPUT:
  Ethylene: 1 ton
  총 배출: 2.26 tCO2/ton
```

#### After NCC-H2
```
INPUT:
  Naphtha (원료):          105 GJ/ton (변화 없음)
  Green H2:                0.18 ton/ton (21.6 GJ) → 0.0 tCO2/ton ✅
  Grid Electricity:        21.8 kWh/ton → 0.10 tCO2/ton ❌ (여전히)

OUTPUT:
  Ethylene: 1 ton
  총 배출: 0.10 tCO2/ton (96% 감축)

OPTION: RE PPA 추가
  Grid → RE Electricity:   21.8 kWh/ton → 0.005 tCO2/ton ✅
  총 배출: 0.005 tCO2/ton (99.8% 감축)
```

#### After NCC-Electricity
```
INPUT:
  Naphtha (원료):          105 GJ/ton (변화 없음)
  RE Electricity (가열):    3.0 MWh/ton → 0.15 tCO2/ton ✅
  RE Electricity (프로세스): 0.022 MWh/ton → 0.005 tCO2/ton ✅

OUTPUT:
  Ethylene: 1 ton
  총 배출: 0.155 tCO2/ton (93% 감축)
```

### 4.2 Non-NCC 시설 (Aromatics - Benzene 예시)

#### 베이스라인
```
INPUT:
  LNG:                     2.5 GJ/ton  ─┐
  Fuel Gas:                3.2 GJ/ton  ├─ 연소 6.3 GJ/ton
  Byproduct Gas:           0.6 GJ/ton ─┘  → 0.34 tCO2/ton ❌
  Grid Electricity:        9.3 kWh/ton → 0.004 tCO2/ton ❌

OUTPUT:
  Benzene: 1 ton
  총 배출: 0.344 tCO2/ton
```

#### After Heat Pump (60% 적용)
```
INPUT:
  화석연료 (40% 잔여):     2.5 GJ/ton → 0.14 tCO2/ton ❌
  RE Electricity (히트펌프): 0.44 MWh/ton → 0.022 tCO2/ton ✅
  Grid Electricity (프로세스): 9.3 kWh/ton → 0.004 tCO2/ton ❌

OUTPUT:
  Benzene: 1 ton
  총 배출: 0.166 tCO2/ton (52% 감축)

NOTE: Heat Pump은 60%만 적용 가능 (온도 제약)
      나머지 40%는 감축 불가능 (고온 공정)
```

---

## 5. 기술 선택 논리 (최적화)

### 5.1 NCC 시설 (상호 배타적)

**옵션 1: NCC-H2**
```
CAPEX: $1440 M$/MtCO2 (2030)
H2 소비: 0.18 ton/ton (현재) → 0.25-0.30 ton/ton (권장)
MACC: $115/tCO2 (현재, 잘못됨) → $467-570/tCO2 (재계산)
감축: 2.26 tCO2/ton (100%)
```

**옵션 2: NCC-Electricity**
```
CAPEX: $1560 M$/MtCO2 (2030)
전력 소비: 3.0 MWh/ton
MACC: $117/tCO2 (현재) → $217/tCO2 (재계산)
감축: 2.11 tCO2/ton (93%)
```

**최적 선택** (에너지 기반):
- ✅ **NCC-Electricity** ($217 << $467-570)
- NCC-H2는 수소 가격이 매우 낮아지거나 (< $2/kg) 전력 가격이 매우 높아질 때만 선택

**추가 옵션: RE PPA** (병행 가능)
```
CAPEX: $0
MACC: $50-100/tCO2 (2030, RE 가격에 따라)
감축: 0.095 tCO2/ton (전력 배출만)
```

### 5.2 Non-NCC 시설

**유일한 옵션: Heat Pump**
```
CAPEX: $720 M$/MtCO2 (2030)
적용률: 10-60% (제품군별)
MACC: $100-200/tCO2
감축: 화석연료 연소 배출의 60-90%
```

---

## 6. 모델 제약 및 개선 가능성

### 6.1 현재 모델 제약

1. **RE PPA는 NCC만 적용**:
   - 코드: `modules/macc.py` line 408-411
   - 주석: "User specified: RE is only applied to NCC"
   - 질문: 왜 Non-NCC 시설은 RE PPA를 사용할 수 없는가?

2. **Heat Pump은 RE 전력 자동 가정**:
   - 코드: `modules/macc.py` line 191
   - Heat Pump은 재생에너지 전력만 사용 (grid 옵션 없음)
   - 즉, Heat Pump 도입 = 자동으로 RE 전력 구매

3. **NCC 기술 상호 배타적**:
   - 코드: `modules/optimization_v2.py` line 181-203
   - 업계 전체가 NCC-H2 또는 NCC-Electricity 중 하나만 선택
   - 현실: 시설별로 다른 선택 가능할 것

### 6.2 개선 가능성

#### 개선 1: RE PPA를 모든 시설에 확대
```python
# 현재 (NCC만)
ncc_facilities = self.df_baseline[
    self.df_baseline['product'].apply(is_ncc_facility)
]

# 개선 (모든 시설)
all_facilities = self.df_baseline  # 모든 시설의 전력 배출 대상
```

**영향**:
- RE PPA 감축 잠재량 증가 (0.4 MtCO2 → 1.5 MtCO2 추정)
- 비용 효과적 (CAPEX=0)

#### 개선 2: Heat Pump + Grid 옵션 추가
```python
# 현재 (RE만)
re_ef = 0.05  # tCO2/MWh (고정)

# 개선 (Grid 옵션 추가)
if use_re:
    electricity_ef = 0.05  # RE
else:
    electricity_ef = grid_ef  # Grid (년도별 변화)
```

**영향**:
- 초기 단계 (2025-2030): Grid 전력 사용 가능 → CAPEX만 부담
- 후기 단계 (2040-2050): Grid 탈탄소화 → RE 전환

#### 개선 3: NCC 기술 시설별 선택
```python
# 현재 (업계 전체 하나만)
industry_ncc_choice = 'NCC-H2'  # or 'NCC-Electricity'

# 개선 (시설별 선택)
for facility in ncc_facilities:
    if facility_cost_optimal == 'NCC-H2':
        deploy NCC-H2
    else:
        deploy NCC-Electricity
```

**영향**:
- 더 realistic한 기술 믹스
- 총 비용 감소

---

## 7. 요약

### 기술별 적용 대상

| 기술 | 적용 시설 | 대체 대상 | 감축 잠재량 |
|------|-----------|-----------|-------------|
| **NCC-H2** | NCC (Ethylene 등) | 화석연료 연소 (고온) | 24.7 MtCO2 (2030) |
| **NCC-Electricity** | NCC (Ethylene 등) | 화석연료 연소 (고온) | 24.5 MtCO2 (2030) |
| **RE PPA** | NCC 전력 | Grid → RE 전력 | 0.4 MtCO2 (2030) |
| **Heat Pump** | Non-NCC (BTX 등) | 화석연료 연소 (중저온) | 2-3 MtCO2 (2030) |

### 시설별 감축 경로

**NCC 시설** (Ethylene):
```
베이스라인: 2.26 tCO2/ton

경로 A (NCC-H2 + RE PPA):
  → NCC-H2: 0.10 tCO2/ton (96% 감축)
  → RE PPA: 0.005 tCO2/ton (99.8% 감축)
  비용: $467-570/tCO2 (NCC-H2) + $50-100/tCO2 (RE PPA)

경로 B (NCC-Elec) ✅ 권장:
  → NCC-Electricity: 0.155 tCO2/ton (93% 감축)
  비용: $217/tCO2 (훨씬 저렴!)
```

**Non-NCC 시설** (Aromatics):
```
베이스라인: 0.34 tCO2/ton

경로 (Heat Pump):
  → Heat Pump (60% 적용): 0.17 tCO2/ton (50% 감축)
  비용: $100-200/tCO2

NOTE: 40%는 고온 공정으로 감축 불가
```

---

**Status**: ✅ **기술 적용 논리 명확화 완료**

**핵심 발견**:
- NCC 시설: NCC-H2 vs NCC-Electricity (상호 배타적)
- Non-NCC 시설: Heat Pump (제품군별 10-60% 적용)
- RE PPA: 현재는 NCC 전력만, 모든 시설로 확대 가능
