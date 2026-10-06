from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "data" / "training_incidents.csv"
TEST = ROOT / "data" / "challenge_test_incidents.csv"
MODELS = ROOT / "models"
RESULTS = ROOT / "results"


def build_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=4000)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
    ])


def apply_critical_guardrail(text, predicted_severity):
    terms = [
        "production outage", "all users", "complete service failure",
        "revenue-impacting", "critical customer path", "possible account compromise",
        "sensitive exports", "primary file system is unavailable", "cannot be served",
        "orders cannot be saved", "unable to access"
    ]
    lower = text.lower()
    return "P1" if any(term in lower for term in terms) else predicted_severity


def main():
    train = pd.read_csv(TRAIN)
    test = pd.read_csv(TEST)
    category_model = build_pipeline().fit(train["text"], train["category"])
    severity_model = build_pipeline().fit(train["text"], train["severity"])

    MODELS.mkdir(exist_ok=True)
    joblib.dump(category_model, MODELS / "category_model.joblib")
    joblib.dump(severity_model, MODELS / "severity_model.joblib")

    cat_pred = category_model.predict(test["text"])
    raw_sev = severity_model.predict(test["text"])
    sev_pred = [apply_critical_guardrail(t, p) for t, p in zip(test["text"], raw_sev)]

    cat_probs = category_model.predict_proba(test["text"]).max(axis=1)
    human_review = [(c < 0.30) or (s == "P1") for c, s in zip(cat_probs, sev_pred)]
    auto_mask = [not x for x in human_review]

    results = {
        "test_samples": int(len(test)),
        "category_accuracy": round(float(accuracy_score(test["category"], cat_pred)), 3),
        "category_macro_f1": round(float(f1_score(test["category"], cat_pred, average="macro")), 3),
        "severity_accuracy_hybrid": round(float(accuracy_score(test["severity"], sev_pred)), 3),
        "severity_macro_f1_hybrid": round(float(f1_score(test["severity"], sev_pred, average="macro")), 3),
        "human_review_rate": round(sum(human_review) / len(human_review), 3),
        "automatic_route_rate": round(sum(auto_mask) / len(auto_mask), 3),
        "automatic_route_category_accuracy": round(float(accuracy_score(test.loc[auto_mask, "category"], cat_pred[auto_mask])), 3),
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "evaluation_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    labels = ["compute", "database", "network", "security", "storage"]
    pd.DataFrame(confusion_matrix(test["category"], cat_pred, labels=labels), index=labels, columns=labels).to_csv(RESULTS / "category_confusion_matrix.csv")
    sev_labels = ["P1", "P2", "P3", "P4"]
    pd.DataFrame(confusion_matrix(test["severity"], sev_pred, labels=sev_labels), index=sev_labels, columns=sev_labels).to_csv(RESULTS / "severity_confusion_matrix.csv")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
