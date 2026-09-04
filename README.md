# AI 기반 토양 오염 확산 예측 및 흡착제 최적화

## 프로젝트 소개

모의 토양 환경에서 색소물의 확산과 정화 과정을 RGB 센서로 측정하고, 축적된 CSV 데이터를 이용해 AI 예측 모델을 학습하는 과학 동아리 연구입니다.

모래와 화분용 흙을 혼합한 토양에 색소물을 투입한 뒤 제올라이트 5A, 제올라이트 13X, 활성탄을 각각 적용합니다. 실험 데이터가 늘어날 때마다 모델을 다시 학습하고 성능을 평가하여, 색소물 정화에 가장 적합한 흡착제와 조건을 찾습니다.

> 색소물은 실제 토양 오염 물질을 단순화한 모의 오염원입니다. 결과를 실제 환경에 적용하려면 실제 오염 물질과 토양을 이용한 추가 검증이 필요합니다.

## 사용 기술과 역할

GitHub는 Python 사용을 제한하거나 비권장하지 않습니다. 이 프로젝트에서는 다음과 같이 역할을 나눕니다.

| 도구 | 역할 |
|---|---|
| Python | CSV 처리, 모델 학습, 예측 및 시각화 |
| pandas | 측정 데이터 정리와 분석 |
| scikit-learn | Random Forest 모델 학습과 평가 |
| Streamlit | Python만으로 실행되는 사용자 화면 |
| VS Code | 코드 작성과 로컬 실행 |
| GitHub | 코드 저장, 버전 관리 및 동아리 협업 |

GitHub Pages는 정적 웹사이트용이므로 Python 코드를 직접 실행할 수 없습니다. 이 프로젝트의 화면은 로컬에서 Streamlit으로 실행하며, 나중에 필요하면 Python을 지원하는 별도의 배포 서비스를 연결할 수 있습니다. 현재 단계에서는 JavaScript나 Unity가 필요하지 않습니다.

## 연구 목표

- 대조군과 제올라이트 5A·13X·활성탄 처리군을 비교합니다.
- RGB 측정값을 이용해 색소물의 확산과 제거 정도를 수치화합니다.
- 시간, 토양 배합비, 흡착제 종류 및 투입량에 따른 정화 효과를 분석합니다.
- Random Forest 회귀 모델로 특정 조건에서의 RGB 값을 예측합니다.
- 실험 데이터가 추가될 때마다 모델을 재학습하여 성능 변화를 확인합니다.

## CSV 필수 열

```csv
experiment_id,sand_ratio,potting_soil_ratio,adsorbent,adsorbent_mass_g,dye_concentration,dye_volume_ml,time_min,position,r,g,b
```

흡착제 이름은 `none`, `zeolite_5a`, `zeolite_13x`, `activated_carbon`으로 기록합니다. 모든 실험 회차에는 고유한 `experiment_id`를 부여합니다.

## AI 모델 설계

초기 데이터는 표 형식이며 양이 많지 않을 것으로 예상되므로 Random Forest 회귀 모델을 기준 모델로 사용합니다. 입력값은 토양 비율, 흡착제 종류와 양, 색소물 조건, 경과 시간, 측정 위치이고 예측값은 R·G·B입니다.

평가 지표는 MAE, RMSE, R²를 사용합니다. 같은 실험에서 나온 시간별 측정값이 학습용과 평가용에 함께 들어가면 성능이 실제보다 좋아 보일 수 있으므로, 데이터는 행 단위가 아니라 **실험 회차(`experiment_id`) 단위**로 분리합니다.

## 프로젝트 구조

```text
integral_team1/
├── app.py
├── data/raw/sample_measurements.csv
├── models/
├── src/
│   ├── modeling.py
│   └── train.py
├── requirements.txt
└── README.md
```

## 실행 방법

Python 3.10 이상을 권장합니다.

```bash
python -m venv .venv
```

Windows PowerShell에서 가상환경을 활성화합니다.

```powershell
.venv\Scripts\Activate.ps1
```

필요한 패키지를 설치하고 Streamlit 화면을 실행합니다.

```bash
pip install -r requirements.txt
streamlit run app.py
```

화면 없이 모델만 학습하려면 다음을 실행합니다.

```bash
python src/train.py --data data/raw/sample_measurements.csv
```

## 실험 통제 조건

- 토양 총질량과 모래·화분흙 배합비
- 색소물 종류, 농도 및 부피
- 흡착제 입자 크기와 투입 방식
- 용기 크기와 모양
- RGB 센서 거리, 각도, 조명 및 측정 위치
- 측정 시간 간격, 온도 및 초기 수분량

각 조건은 가능하면 3회 이상 반복하고 평균과 표준편차를 함께 기록합니다. RGB 값은 조명의 영향을 받으므로 흰색 기준 시료와 흡착제가 없는 대조군을 함께 측정합니다.

## 개발 계획

- [x] 프로젝트 설명과 기본 구조 작성
- [x] CSV 예시 파일 작성
- [x] Random Forest 기준 모델 작성
- [x] Streamlit 기본 화면 작성
- [ ] 실제 RGB 센서와 CSV 저장 방식 확정
- [ ] 예비 실험 및 RGB-농도 검량선 작성
- [ ] 실제 반복 측정 데이터 수집
- [ ] 정화 효율 계산식 확정
- [ ] 흡착제별 최적 조건 탐색 기능 구현
- [ ] 실제 환경 적용 가능성과 한계 분석

## 주의사항

- 예시 CSV의 수치는 프로그램 작동 확인용 가상 데이터이며 연구 결과로 사용하지 않습니다.
- 색소물 실험 결과를 실제 중금속이나 유기 오염 물질의 정화 성능으로 바로 해석하지 않습니다.
- 원본 데이터는 수정하지 않고 `data/raw/`에 보존합니다.
- 흡착제 분말은 지도교사의 안전 지침에 따라 취급합니다.
- 모델 정확도와 함께 데이터 수, 오차 및 적용 한계를 보고합니다.
