import pandas as pd
import streamlit as st

from src.modeling import FEATURES, TARGETS, save_model, train_and_evaluate

st.set_page_config(page_title="토양 정화 AI", page_icon="🌱", layout="wide")
st.title("흡착제 질량별 모의 토양오염 측정 데이터 분석")
st.caption("제올라이트 5A·13X·활성탄의 질량별 RGB 및 투명도 측정값을 비교합니다. 색소물은 모의 오염원입니다.")

uploaded = st.file_uploader("실험 CSV 업로드", type="csv")
source = uploaded if uploaded is not None else "data/raw/sample_measurements.csv"

try:
    data = pd.read_csv(source, comment="#")
    needed = ["experiment_id", *FEATURES, *TARGETS]
    missing = [c for c in needed if c not in data.columns]
    if missing:
        st.error(f"CSV에 필요한 열이 없습니다: {', '.join(missing)}")
        st.stop()

    data = data.copy()
    for column in ["adsorbent_mass_g", "dye_concentration", "time_min", *TARGETS]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.dropna(subset=needed)
    if data.empty:
        st.warning("그래프로 표시할 유효한 측정 데이터가 없습니다.")
        st.stop()

    st.info("RGB·투명도 값은 정화 효율(%)이 아닙니다. 실제 정화율 분석에는 농도 검량선이 필요합니다.")
    st.subheader("실험 조건 선택")
    col1, col2, col3 = st.columns(3)
    adsorbents = sorted(data["adsorbent"].unique().tolist())
    selected = col1.multiselect("흡착제", adsorbents, default=adsorbents)
    times = sorted(data["time_min"].unique().tolist())
    selected_time = col2.selectbox("경과 시간 (분)", times, index=len(times)-1)
    concentrations = sorted(data["dye_concentration"].unique().tolist())
    selected_conc = col3.selectbox("염료 농도 (기록 단위)", concentrations)

    filtered = data[
        data["adsorbent"].isin(selected)
        & (data["time_min"] == selected_time)
        & (data["dye_concentration"] == selected_conc)
    ]
    st.subheader("측정 데이터")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.caption(f"전체 {len(data)}행 / 선택된 조건 {len(filtered)}행 · 독립 실험 {data['experiment_id'].nunique()}회")

    if not filtered.empty:
        st.subheader("흡착제 질량별 센서 측정값")
        metric = st.selectbox("표시할 센서 항목", TARGETS, format_func=lambda x: {
            "r": "R (빨강)", "g": "G (초록)", "b": "B (파랑)", "clear": "투명도 (clear)"
        }[x])
        # pandas 버전에 관계없이 평균과 반복 측정 수를 명시적으로 계산
        grouped = filtered.groupby(["adsorbent_mass_g", "adsorbent"], as_index=False).agg(
            mean_value=(metric, "mean"), measurement_count=(metric, "size")
        )
        chart_data = grouped.pivot(index="adsorbent_mass_g", columns="adsorbent", values="mean_value")
        st.line_chart(chart_data, x_label="흡착제 질량 (g)", y_label=f"{metric} 센서값")
        st.caption("동일 질량·흡착제 조건의 평균값을 연결한 그래프입니다. 측정점이 적으면 추세를 해석할 수 없습니다.")
        st.subheader("흡착제별 비교")
        st.bar_chart(filtered.groupby("adsorbent")[TARGETS].mean(), y_label="평균 센서값")
        st.subheader("질량별 집계")
        st.dataframe(grouped, hide_index=True, use_container_width=True)

    st.divider()
    st.subheader("Random Forest 예측 모델")
    st.caption("실험 회차별로 학습·평가 데이터를 분리합니다. 충분한 독립 실험 데이터가 필요합니다.")
    if st.button("모델 학습 및 평가", type="primary"):
        try:
            with st.spinner("모델 학습 중..."):
                model, metrics, comparison = train_and_evaluate(data)
                saved_path = save_model(model)
            columns = st.columns(3)
            for column, (name, value) in zip(columns, metrics.items()):
                column.metric(name, "평가 불가" if pd.isna(value) else f"{value:.3f}")
            st.caption("MAE와 RMSE는 네 센서 항목을 함께 평가한 값입니다. R²는 평가 표본이 적으면 불안정합니다.")
            st.subheader("실제 측정값과 AI 예측값 비교")
            target = st.selectbox("비교 항목", TARGETS, key="prediction_target")
            comparison_plot = comparison[[target, f"pred_{target}"]].rename(
                columns={target: "실제값", f"pred_{target}": "예측값"}
            )
            st.scatter_chart(comparison_plot, x="실제값", y="예측값", x_label="실제 측정값", y_label="AI 예측값")
            st.dataframe(comparison, use_container_width=True, hide_index=True)
            st.success(f"학습된 모델 저장: {saved_path}")
        except ValueError as error:
            st.warning(str(error))
        except Exception as error:
            st.error(f"학습 중 오류가 발생했습니다: {error}")
except Exception as error:
    st.error(f"데이터를 불러오지 못했습니다: {error}")
