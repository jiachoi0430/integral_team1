import pandas as pd
import streamlit as st
from src.modeling import save_model, train_and_evaluate

st.set_page_config(page_title="토양 정화 AI", page_icon="🌱", layout="wide")
st.title("흡착제 질량별 모의 토양오염 정화 측정값 예측")
st.caption("흡착제 종류·질량·염료 농도·시간으로 RGB 및 투명도 측정값을 예측합니다.")
uploaded = st.file_uploader("실험 CSV 업로드", type="csv")
source = uploaded if uploaded is not None else "data/raw/sample_measurements.csv"

try:
    data = pd.read_csv(source, comment="#")
    st.subheader("측정 데이터")
    st.dataframe(data, use_container_width=True)
    if st.button("모델 학습 및 평가", type="primary"):
        try:
            with st.spinner("모델 학습 중..."):
                model, metrics, comparison = train_and_evaluate(data)
                saved_path = save_model(model)
            cols = st.columns(3)
            for column, (name, value) in zip(cols, metrics.items()):
                column.metric(name, "평가 불가" if pd.isna(value) else f"{value:.3f}")
            st.subheader("실제값과 예측값")
            st.dataframe(comparison, use_container_width=True)
            st.success(f"모델 저장: {saved_path}")
            st.info("RGB·투명도 예측은 정화 효율(%) 예측과 다릅니다. 실제 농도 검량이 필요합니다.")
        except ValueError as error:
            st.warning(str(error))
except Exception as error:
    st.error(f"CSV를 불러올 수 없습니다: {error}")
