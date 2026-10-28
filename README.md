# AI 기반 모의 토양오염 정화 효과 비교 및 흡착제 질량 최적화

## 프로젝트 개요

제올라이트 5A·13X와 활성탄의 투입 질량에 따른 모의 토양오염 정화 효과를 비교하고, RGB 및 투명도 센서 측정 데이터를 활용하여 Random Forest 회귀 예측 모델을 개발하는 과학 동아리 연구이다.

모래 1 kg과 화분흙 0.4 kg을 혼합한 토양에 색소물을 투입하고, 흡착제 종류·질량·염료 농도·경과 시간에 따른 측정값을 비교한다. **측정 위치는 AI 입력 변수에서 제외**하며, 동일한 센서 배치와 조명 조건을 유지한다.

> 색소물은 모의 오염원이다. RGB 및 투명도 변화는 정화 효율(%)과 동일하지 않으며, 실제 제거율 계산에는 농도 검량선 등 추가 검증이 필요하다.

## 연구 목표

1. 제올라이트 5A, 13X, 활성탄과 무처리 대조군을 비교한다.
2. **흡착제 질량(g)** 변화에 따른 센서값 차이를 분석한다.
3. 염료 농도와 경과 시간이 측정값에 미치는 영향을 확인한다.
4. Random Forest 모델로 RGB 및 투명도 값을 예측한다.
5. 실험과 검증 데이터가 충분히 축적되면 정화 성능과 사용량을 고려한 권장 흡착제 질량 범위를 탐색한다.

## 데이터 구조

원본 예시 파일: `data/raw/sample_measurements.csv`

현재 파일의 열 구조는 다음과 같다.

```csv
experiment_id,adsorbent,adsorbent_mass_g,dye_concentration,time_min,r,g,b,clear
```

| 열 | 설명 |
|---|---|
| `experiment_id` | 실험 회차 식별자 |
| `adsorbent` | 흡착제 종류 (`none`, `zeolite_5a`, `zeolite_13x`, `activated_carbon`) |
| `adsorbent_mass_g` | 흡착제 투입 질량(g), 핵심 독립변수 |
| `dye_concentration` | 초기 색소 농도(단위·정의는 실험 계획에서 확정) |
| `time_min` | 경과 시간(분) |
| `r`, `g`, `b` | RGB 센서 측정값 |
| `clear` | 투명도 관련 측정값(센서 방식·척도 확인 필요) |

현재 예시 데이터는 모델 작동을 확인하기 위한 **가상 데이터**이며 실제 실험 결과가 아니다. CSV 안의 설명 행(예: `#실험 번호,...`)은 일반 데이터로 읽힐 수 있으므로 학습 전 제거하거나 별도 문서로 옮긴다.

### 실험 통제 조건

- 모래 1 kg + 화분흙 0.4 kg 고정
- 동일한 색소 종류와 투입 방식
- 동일한 용기 및 측정 장치
- RGB 센서의 위치·거리·각도·조명 고정
- 흡착제 입자 크기와 처리 방법의 일관성 유지
- 온도·수분량·측정 간격 기록 및 관리

위치는 **변화시키는 입력 변수가 아니라 통제 조건**이다. 흡착제 질량을 단계적으로 변화시키고 다른 조건은 가능한 한 일정하게 유지한다. 각 조건은 반복 실험하여 측정 오차를 확인한다.

## AI 예측 모델

- 도구: Python, pandas, scikit-learn, matplotlib, Streamlit
- 알고리즘: `RandomForestRegressor`
- 입력값(X): `adsorbent`, `adsorbent_mass_g`, `dye_concentration`, `time_min`
- 출력값(y): `r`, `g`, `b`, `clear`
- 범주형 전처리: `OneHotEncoder`
- 평가 지표: MAE, RMSE, R²(검증 데이터 규모에 맞게 해석)

동일 실험에서 반복 측정한 행이 학습과 평가에 동시에 포함되면 성능이 과대평가될 수 있다. 따라서 `experiment_id`를 기준으로 학습·검증 데이터를 분리한다.

### 질량 최적화

실제 실험에서 측정한 질량 범위 내에서 흡착제별 예측값을 비교한다. 예측 모델이 제안한 조건은 별도 실험으로 검증한다. 정화 효율(%)을 직접 예측하려면 RGB/투명도와 실제 잔류 농도 사이의 검량 관계를 먼저 확보해야 한다.

## 프로젝트 구조

```text
integral_team1/
├── app.py
├── data/
│   └── raw/
│       └── sample_measurements.csv
├── models/
├── src/
│   ├── modeling.py
│   └── train.py
├── requirements.txt
└── README.md
```

## 실행 방법

Python 3.10 이상을 권장한다.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

모델만 학습할 때:

```powershell
python src/train.py --data data/raw/sample_measurements.csv
```

**주의:** 기존 Python 코드가 이전 CSV 열 구조를 참조한다면 실행 전에 `src/modeling.py`, `src/train.py` 등을 새 구조에 맞게 수정해야 한다. 현재 예시 데이터 한 행만으로는 의미 있는 AI 학습이나 성능 평가가 불가능하다.

## 개발 계획

- [x] 기본 프로젝트 및 예시 CSV 생성
- [x] 위치 변수 제거 및 흡착제 질량 중심 데이터 구조 정의
- [x] README 연구 목표·변수 설명 수정
- [ ] CSV 설명 행 정리 및 `clear` 측정 정의 확정
- [ ] 기존 모델 코드와 CSV 스키마 일치시키기
- [ ] 실제 RGB 센서 데이터 수집
- [ ] 반복 실험 및 대조군 데이터 확보
- [ ] 농도 검량선 검토
- [ ] Random Forest 학습·검증
- [ ] 흡착제별 질량 최적화
- [ ] AI 추천 조건의 실제 실험 검증

## 연구상 유의사항

- 가상 데이터로부터 실제 정화 성능에 관한 결론을 내리지 않는다.
- 원본 데이터는 `data/raw/`에 보존한다.
- 색소물의 제거 결과를 중금속 등 실제 오염물질의 제거 성능으로 일반화하지 않는다.
- 모델의 예측 범위, 데이터 수, 오차 및 불확실성을 함께 보고한다.
- 실험은 지도교사의 안전 지침을 따른다.
