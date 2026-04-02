import os, json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                              recall_score, mean_absolute_error, r2_score)
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier, MLPRegressor
from xgboost import XGBClassifier
from preprocessing import load_dataset, get_disease_data, get_glucose_data

os.makedirs("models", exist_ok=True)

df = load_dataset()

disease_targets = ["Diabetes_Diagnosis", "hypertension", "cardiovascular", "kidney"]
X_raw = df.drop(columns=disease_targets)
y     = df[disease_targets]

X_train_raw, X_test_raw, y_train, y_test = train_test_split(
    X_raw, y, test_size=0.2, random_state=42)

scaler  = StandardScaler()
X_train = pd.DataFrame(scaler.fit_transform(X_train_raw), columns=X_train_raw.columns)
X_test  = pd.DataFrame(scaler.transform(X_test_raw),      columns=X_test_raw.columns)

joblib.dump(scaler, "models/scaler.pkl")
features = X_train.columns.tolist()
print(f"Features used for training: {features}")

# ── Save metrics here ──────────────────────────────────────────────────────
all_metrics = {}

for col in disease_targets:
    print(f"\n{'='*50}")
    print(f"  Training models for: {col}")
    print(f"{'='*50}")
    all_metrics[col] = {}

    for name, model in [
        ("LogisticRegression", LogisticRegression(max_iter=500)),
        ("RandomForest",       RandomForestClassifier(n_estimators=100, random_state=42)),
        ("XGBoost",            XGBClassifier(eval_metric="logloss", random_state=42, base_score=0.5)),
        ("MLP_NeuralNetwork",  MLPClassifier(
            hidden_layer_sizes=(128,64,32), activation="relu", solver="adam",
            alpha=0.001, batch_size=32, learning_rate="adaptive", max_iter=300,
            early_stopping=True, validation_fraction=0.1, n_iter_no_change=15,
            random_state=42, verbose=False)),
    ]:
        model.fit(X_train, y_train[col])
        y_pred = model.predict(X_test)
        acc  = accuracy_score(y_test[col], y_pred)
        f1   = f1_score(y_test[col], y_pred, zero_division=0)
        prec = precision_score(y_test[col], y_pred, zero_division=0)
        rec  = recall_score(y_test[col], y_pred, zero_division=0)
        print(f"{name:<22} — Acc: {acc:.4f} | F1: {f1:.4f} | "
              f"Precision: {prec:.4f} | Recall: {rec:.4f}")

        # Save model
        key_map = {"LogisticRegression":"logreg","RandomForest":"rf",
                   "XGBoost":"xgb","MLP_NeuralNetwork":"mlp"}
        joblib.dump(model, f"models/{col}_{key_map[name]}.pkl")

        # Store metrics
        all_metrics[col][name] = {
            "accuracy": round(acc, 4), "f1": round(f1, 4),
            "precision": round(prec, 4), "recall": round(rec, 4)
        }

print("\n✅ All classification models trained and saved.")

# ── GLUCOSE REGRESSION ─────────────────────────────────────────────────────
print(f"\n{'='*50}")
print("  Training Glucose Regression Models")
print(f"{'='*50}")

glucose_drop  = ["Glucose_level", "hypertension", "cardiovascular", "kidney"]
X_glucose_raw = df.drop(columns=glucose_drop)
y_glucose     = df["Glucose_level"]

X_train_g_raw, X_test_g_raw, y_train_g, y_test_g = train_test_split(
    X_glucose_raw, y_glucose, test_size=0.2, random_state=42)

scaler_glucose = StandardScaler()
X_train_g = pd.DataFrame(scaler_glucose.fit_transform(X_train_g_raw), columns=X_train_g_raw.columns)
X_test_g  = pd.DataFrame(scaler_glucose.transform(X_test_g_raw),      columns=X_test_g_raw.columns)

all_metrics["Glucose_Regression"] = {}

for name, model in [
    ("LinearRegression", LinearRegression()),
    ("MLP_NeuralNetwork", MLPRegressor(
        hidden_layer_sizes=(128,64,32), activation="relu", solver="adam",
        alpha=0.001, batch_size=32, learning_rate="adaptive", max_iter=300,
        early_stopping=True, validation_fraction=0.1, n_iter_no_change=15,
        random_state=42, verbose=False)),
]:
    model.fit(X_train_g, y_train_g)
    y_pred_g = model.predict(X_test_g)
    mae = mean_absolute_error(y_test_g, y_pred_g)
    r2  = r2_score(y_test_g, y_pred_g)
    print(f"{name:<22} — MAE: {mae:.4f} | R²: {r2:.4f}")
    if name == "LinearRegression":
        joblib.dump(model, "models/glucose_regression.pkl")
        joblib.dump(scaler_glucose, "models/glucose_scaler.pkl")
    else:
        joblib.dump(model, "models/glucose_mlp.pkl")
    all_metrics["Glucose_Regression"][name] = {
        "MAE": round(mae, 4), "R2": round(r2, 4)
    }

# ── SAVE METRICS JSON ──────────────────────────────────────────────────────
metrics_path = "models/model_metrics.json"
with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(all_metrics, f, indent=2)
print(f"\n✅ Metrics saved to {metrics_path}")
print("✅ All models complete!")


# ═══════════════════════════════════════════════════════════════════════════
# DEEP LEARNING — TENSORFLOW MLP
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n{'='*50}")
print("  Training TensorFlow MLP Models")
print(f"{'='*50}")

try:
    import tensorflow as tf
    import keras
    from keras import layers
    import numpy as np

    tf.random.set_seed(42)

    for col in disease_targets:
        print(f"\n--- TF MLP: {col} ---")
        y_train_col = y_train[col].values
        y_test_col  = y_test[col].values

        # Build model
        model_tf = keras.Sequential([
            keras.layers.Input(shape=(X_train.shape[1],)),
            keras.layers.Dense(128, activation="relu"),
            keras.layers.BatchNormalization(),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(64, activation="relu"),
            keras.layers.BatchNormalization(),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(32, activation="relu"),
            keras.layers.Dense(1, activation="sigmoid")
        ])
        model_tf.compile(
            optimizer=keras.optimizers.Adam(0.001),
            loss="binary_crossentropy",
            metrics=["accuracy"]
        )

        early_stop = keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=10, restore_best_weights=True)

        model_tf.fit(
            X_train.values, y_train_col,
            validation_split=0.1,
            epochs=100, batch_size=32,
            callbacks=[early_stop],
            verbose=0
        )

        y_pred_tf = (model_tf.predict(X_test.values, verbose=0) > 0.5).astype(int).flatten()
        acc  = accuracy_score(y_test_col, y_pred_tf)
        f1   = f1_score(y_test_col, y_pred_tf, zero_division=0)
        prec = precision_score(y_test_col, y_pred_tf, zero_division=0)
        rec  = recall_score(y_test_col, y_pred_tf, zero_division=0)
        print(f"TF_MLP               — Acc: {acc:.4f} | F1: {f1:.4f} | "
              f"Precision: {prec:.4f} | Recall: {rec:.4f}")

        # Save as .keras format
        model_tf.save(f"models/{col}_tf_mlp.keras")

        all_metrics[col]["TF_MLP"] = {
            "accuracy": round(acc,4), "f1": round(f1,4),
            "precision": round(prec,4), "recall": round(rec,4)
        }

    print("\n✅ TensorFlow MLP models saved.")

except ImportError:
    print("⚠️ TensorFlow not installed. Run: pip install tensorflow")
except Exception as e:
    print(f"⚠️ TensorFlow training failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# DEEP LEARNING — TABNET (pytorch-tabnet)
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n{'='*50}")
print("  Training TabNet Models")
print(f"{'='*50}")

try:
    from pytorch_tabnet.tab_model import TabNetClassifier
    import numpy as np

    for col in disease_targets:
        print(f"\n--- TabNet: {col} ---")
        y_train_col = y_train[col].values
        y_test_col  = y_test[col].values

        tabnet = TabNetClassifier(
            n_d=16, n_a=16,
            n_steps=3,
            gamma=1.3,
            n_independent=2, n_shared=2,
            momentum=0.02,
            optimizer_fn=__import__('torch').optim.Adam,
            optimizer_params={"lr": 1e-3},
            scheduler_fn=__import__('torch').optim.lr_scheduler.StepLR,
            scheduler_params={"step_size": 10, "gamma": 0.9},
            mask_type="entmax",
            verbose=0,
            seed=42
        )

        tabnet.fit(
            X_train=X_train.values.astype(np.float32),
            y_train=y_train_col,
            eval_set=[(X_test.values.astype(np.float32), y_test_col)],
            patience=15,
            max_epochs=100,
            batch_size=256,
            virtual_batch_size=128,
            eval_metric=["accuracy"]
        )

        y_pred_tn = tabnet.predict(X_test.values.astype(np.float32))
        acc  = accuracy_score(y_test_col, y_pred_tn)
        f1   = f1_score(y_test_col, y_pred_tn, zero_division=0)
        prec = precision_score(y_test_col, y_pred_tn, zero_division=0)
        rec  = recall_score(y_test_col, y_pred_tn, zero_division=0)
        print(f"TabNet               — Acc: {acc:.4f} | F1: {f1:.4f} | "
              f"Precision: {prec:.4f} | Recall: {rec:.4f}")

        tabnet.save_model(f"models/{col}_tabnet")

        all_metrics[col]["TabNet"] = {
            "accuracy": round(acc,4), "f1": round(f1,4),
            "precision": round(prec,4), "recall": round(rec,4)
        }

    print("\n✅ TabNet models saved.")

except ImportError:
    print("⚠️ TabNet not installed. Run: pip install pytorch-tabnet")
except Exception as e:
    print(f"⚠️ TabNet training failed: {e}")


# ── UPDATE METRICS WITH NEW MODELS ─────────────────────────────────────────
with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(all_metrics, f, indent=2)
print(f"\n✅ Updated metrics saved to {metrics_path}")
print("✅ All training complete!")