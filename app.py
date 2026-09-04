import pandas as pd
import streamlit as st

from src.modeling import save_model, train_and_evaluate

st.set_page_config(page_title="토양 정화 AI", page_icon="🌱", layout="wide")
st.title("토양 오염 확산 예측 및 흡착제 비교")
st.caption("CSV 측정값으로 Random Forest 모델을 다시 학습하고 결과를 확인합니다.")

uploaded = st.file_uploader("RGB 측정 CSV 업로드", type="csv")
source = uploaded if uploaded is not None else "data/raw/sample_measurements.csv"

try:
    data = pd.read_csv(source)
    st.subheader("측정 데이터")
    st.dataframe(data, use_container_width=True)

    if st.button("모델 학습 및 평가", type="primary"):
        with st.spinner("모델을 학습하고 있습니다..."):
            model, metrics, comparison = train_and_evaluate(data)
            saved_path = save_model(model)
        cols = st.columns(3)
        for column, (name, value) in zip(cols, metrics.items()):
            column.metric(name, f"{value:.3f}")
        st.subheader("실제값과 예측값")
        st.dataframe(comparison, use_container_width=True)
        st.success(f"학습된 모델을 {saved_path}에 저장했습니다.")
        st.info("예시 데이터는 모델 구조 확인용입니다. 실제 결론은 반복 실험 데이터로 판단하세요.")
except Exception as error:
    st.error(f"데이터를 처리할 수 없습니다: {error}")
