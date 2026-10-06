# Trained Models

The project uses two scikit-learn pipelines trained by `src/train_model.py`:

- `category_model.joblib`: TF-IDF plus logistic regression for incident category classification.
- `severity_model.joblib`: TF-IDF plus logistic regression for P1-P4 severity prediction.

The binary model artifacts are reproducibly generated from the project training data by running:

```bash
python src/train_model.py
```

Expected SHA-256 hashes for the submitted model artifacts:

- `category_model.joblib`: `c5134b5332267fde1306d71dd6c421bf04a4156dbb8d889991767f16b78e8b1c`
- `severity_model.joblib`: `a36b0b54619f845f0426f1b0ee08aeb0fa868c29048754e78a24ffa3868b7fd4`

The Lambda container expects these files under `models/` at build time.
