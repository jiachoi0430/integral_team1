import argparse
import pandas as pd
from modeling import save_model, train_and_evaluate


def main():
    parser = argparse.ArgumentParser(description="RGB 및 투명도 예측 모델 학습")
    parser.add_argument("--data", default="data/raw/sample_measurements.csv")
    parser.add_argument("--output", default="models/random_forest_rgb_clear.joblib")
    args = parser.parse_args()
    data = pd.read_csv(args.data, comment="#")
    model, metrics, comparison = train_and_evaluate(data)
    output = save_model(model, args.output)
    print("평가 결과:", metrics)
    print("평가 데이터 행 수:", len(comparison))
    print("저장 위치:", output)


if __name__ == "__main__":
    main()
