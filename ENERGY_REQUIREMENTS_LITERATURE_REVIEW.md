# 에틸렌 생산 에너지 소비량 문헌 조사

## 📚 문헌 검토 결과

### 1. 기존 납사 크래킹 (Conventional Naphtha Steam Cracking)

**열 에너지 소비 (Thermal Energy)**:
- **범위**: 26-31 GJ/ton ethylene (일반적)
- **최적**: 18-21 GJ/ton ethylene (best practice)
- **최대**: 40 GJ/ton ethylene (비효율적 플랜트)
- **평균**: ~30 GJ/ton ethylene

**출처**:
- "Olefins from conventional and heavy feedstocks: Energy use in steam cracking" (ScienceDirect)
- "Energy use, CO2 emissions and production costs" studies

**핵심**:
- 이 중 **반응열(stoichiometric heat)**: 6.7 GJ/ton (약 30%)
- 나머지 70%: 분리, 가열, 손실 등

---

### 2. 전기 크래킹 (Electric Cracking)

**전력 소비 (Electricity)**:
- **문헌 데이터**: 명확한 수치 없음
- **간접 추정**:
  - 열 에너지 30 GJ/ton ÷ 3.6 = **8.3 MWh/ton ethylene**
  - 전기 가열 효율 고려 시 **~10 MWh/ton**
- **Green Chemistry 2025 논문**: 전기 크래커 언급하지만 구체적 MWh 명시 안 함

**기존 가정 (13 MWh/ton)**:
- **근거 부족** - 출처 불명확
- **재검토 필요**

**논리적 추정**:
```
열 에너지 30 GJ/ton = 8.33 MWh/ton (thermal)
→ 전기 저항 가열 시: 8.33 MWh (electrical) 필요
→ 효율 손실 고려: 9-10 MWh/ton 합리적
```

---

### 3. 수소 크래킹 (H2-based Cracking)

**수소 소비량**:
- **문헌**: **구체적 수치 없음** - 기술이 아직 상용화되지 않음
- **기존 가정 (0.8 ton H2/ton ethylene)**: 근거 불명확

**논리적 추정**:

#### 방법 1: 열량 기준
```
납사 연소열: 30 GJ/ton ethylene
수소 연소열 (LHV): 120 MJ/kg = 120 GJ/ton H2

필요 수소량 = 30 GJ ÷ 120 GJ/ton = 0.25 ton H2/ton ethylene
```

#### 방법 2: 화학양론 기준
```
C2H4 (ethylene) 분자량: 28 g/mol
H2 필요량 (반응 보조): ?

실제로는 H2를 연료로만 사용 (열 공급)
→ 0.25 ton H2/ton ethylene 합리적
```

#### ⚠️ 문제점:
- **0.8 ton H2/ton**: **과다 추정 가능성 높음**
- 열량 기준으로 **0.2-0.3 ton H2/ton**이 더 합리적

---

## 🔍 현재 모델의 문제점

### 문제 1: 납사 연료비 포함
- **현재**: 납사 연료비($1,575/ton)를 H2/전기 비용과 비교
- **문제**: 납사 원료는 계속 필요하므로 **고정비**
- **해결**: 납사 비용 완전히 제외

### 문제 2: 수소 소비량 과다
- **현재**: 0.8 ton H2/ton ethylene
- **추정**: 0.25 ton H2/ton ethylene (열량 기준)
- **차이**: **3배 이상** 과다 추정

### 문제 3: 전기 소비량 불명확
- **현재**: 13 MWh/ton ethylene
- **추정**: 8-10 MWh/ton ethylene (논리적)
- **근거**: 문헌에서 명확한 수치 없음

### 문제 4: H2 가격 가정
- **현재**: $6/kg (2025) → $1.2/kg (2050)
- **사용자 요청**: **2배 더 비싸게** (즉, $12/kg in 2025)

---

## ✅ 수정 제안

### 1. 납사 비용 제거
```python
# Before (잘못됨)
fuel_diff = h2_cost - naphtha_cost

# After (올바름)
fuel_diff = h2_cost - 0  # 납사는 양쪽 다 동일 (고정비)
```

### 2. 수소 소비량 수정
```
기존: 0.8 ton H2/ton ethylene
수정: 0.3 ton H2/ton ethylene (보수적)
```

### 3. 전기 소비량 재검토
```
기존: 13 MWh/ton ethylene
수정: 10 MWh/ton ethylene (열량 기준)
```

### 4. H2 가격 수정
```
기존: $6/kg (2025) → $1.2/kg (2050)
수정: $12/kg (2025) → $2.4/kg (2050)
```

---

## 📊 수정 후 예상 비용 (2050년 기준)

### NCC-H2:
```
CAPEX: $14/tCO2
OPEX: $0.35/tCO2
H2 비용: 0.3 ton × 1000 kg × $2.4/kg = $720/ton ethylene
배출 감축: 30 GJ × 0.0149 = 0.447 tCO2/ton
Fuel Diff: $720 / 0.447 = $1,610/tCO2

Total MACC = $14 + $0.35 + $1,610 = $1,624/tCO2
```

### NCC-Electricity (with clean grid):
```
CAPEX: $17/tCO2
OPEX: $0.34/tCO2
전력 비용: 10 MWh × $100/MWh = $1,000/ton ethylene
배출 감축: 0.447 - (10 × 0.25) = -2.05 tCO2/ton (오히려 증가!)

→ 재생에너지 필수!
```

---

## 🎯 결론

1. **납사 비용은 완전히 제외**해야 함 (고정비)
2. **수소 소비량 0.8 → 0.3 ton/ton**으로 수정
3. **전기 소비량 13 → 10 MWh/ton**으로 수정
4. **H2 가격 2배 상향** ($6 → $12/kg in 2025)
5. **전기 크래커는 재생에너지 그리드 전제** 필요

이렇게 수정하면 **비용 절감 효과가 사라지고**, 현실적인 MACC가 나옵니다.
