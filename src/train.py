import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

def evaluate_model(name, model, X_test, y_test):
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds, zero_division=0)
    rec = recall_score(y_test, preds, zero_division=0)
    f1 = f1_score(y_test, preds, zero_division=0)
    auc = roc_auc_score(y_test, probs)

    print(f"\n--- {name} Results ---")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall   : {rec:.4f}  (Crucial for scam catch rate)")
    print(f"F1-Score : {f1:.4f}")
    print(f"ROC-AUC  : {auc:.4f}")
    return {"name": name, "model": model, "f1": f1, "recall": rec, "auc": auc}

def build_calibrated_model(base_estimator):
    """Handles scikit-learn parameter variations (estimator vs base_estimator) cleanly."""
    try:
        return CalibratedClassifierCV(estimator=base_estimator, method="isotonic", cv=5)
    except TypeError:
        return CalibratedClassifierCV(base_estimator=base_estimator, method="isotonic", cv=5)

def main():
    data_path = os.path.join("data", "features.csv")
    if not os.path.exists(data_path):
        print(f"Error: Could not find '{data_path}'. Make sure 'src/prepare_data.py' ran successfully.")
        return

    print("Loading extracted features from data/features.csv...")
    df = pd.read_csv(data_path)

    # Ensure clean numeric target
    X = df.drop(columns=["label"])
    y = df["label"].astype(int)
    feature_names = list(X.columns)

    # Stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Dataset split: {len(X_train)} training rows, {len(X_test)} testing rows.")

    # Candidate models
    models = {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, random_state=42))
        ]),
        "Random Forest": RandomForestClassifier(
            n_estimators=150, max_depth=12, random_state=42, n_jobs=-1
        ),
        "XGBoost": XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            eval_metric="logloss",
            random_state=42,
        )
    }

    results = []
    for name, clf in models.items():
        print(f"\nTraining {name}...")
        clf.fit(X_train, y_train)
        res = evaluate_model(name, clf, X_test, y_test)
        results.append(res)

    # Select best model by F1-Score
    best_candidate = max(results, key=lambda x: x["f1"])
    print(f"\nBest Model: {best_candidate['name']}")

    # Apply Probability Calibration
    print("\nApplying Isotonic Calibration...")
    calibrated_clf = build_calibrated_model(best_candidate["model"])
    calibrated_clf.fit(X_train, y_train)

    evaluate_model(f"Calibrated {best_candidate['name']}", calibrated_clf, X_test, y_test)

    # Save artifact
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    save_payload = {
        "model": calibrated_clf,
        "base_model": best_candidate["model"],
        "feature_names": feature_names
    }

    model_path = os.path.join(models_dir, "model.joblib")
    joblib.dump(save_payload, model_path)
    print(f"\nModel package saved to {model_path}!")

if __name__ == "__main__":
    main()