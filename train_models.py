# import os, json
# import joblib
# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# from sklearn.metrics import (accuracy_score, f1_score, precision_score,
#                               recall_score, mean_absolute_error, r2_score)
# from sklearn.linear_model import LogisticRegression, LinearRegression
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.neural_network import MLPClassifier, MLPRegressor
# from xgboost import XGBClassifier
# from preprocessing import load_dataset, get_disease_data, get_glucose_data

# os.makedirs("models", exist_ok=True)

# df = load_dataset()

# disease_targets = ["Diabetes_Diagnosis", "hypertension", "cardiovascular", "kidney"]
# X_raw = df.drop(columns=disease_targets)
# y     = df[disease_targets]

# X_train_raw, X_test_raw, y_train, y_test = train_test_split(
#     X_raw, y, test_size=0.2, random_state=42)

# scaler  = StandardScaler()
# X_train = pd.DataFrame(scaler.fit_transform(X_train_raw), columns=X_train_raw.columns)
# X_test  = pd.DataFrame(scaler.transform(X_test_raw),      columns=X_test_raw.columns)

# joblib.dump(scaler, "models/scaler.pkl")
# features = X_train.columns.tolist()
# print(f"Features used for training: {features}")

# # ── Save metrics here ──────────────────────────────────────────────────────
# all_metrics = {}

# for col in disease_targets:
#     print(f"\n{'='*50}")
#     print(f"  Training models for: {col}")
#     print(f"{'='*50}")
#     all_metrics[col] = {}

#     for name, model in [
#         ("LogisticRegression", LogisticRegression(max_iter=500)),
#         ("RandomForest",       RandomForestClassifier(n_estimators=100, random_state=42)),
#         ("XGBoost",            XGBClassifier(eval_metric="logloss", random_state=42, base_score=0.5)),
#         ("MLP_NeuralNetwork",  MLPClassifier(
#             hidden_layer_sizes=(128,64,32), activation="relu", solver="adam",
#             alpha=0.001, batch_size=32, learning_rate="adaptive", max_iter=300,
#             early_stopping=True, validation_fraction=0.1, n_iter_no_change=15,
#             random_state=42, verbose=False)),
#     ]:
#         model.fit(X_train, y_train[col])
#         y_pred = model.predict(X_test)
#         acc  = accuracy_score(y_test[col], y_pred)
#         f1   = f1_score(y_test[col], y_pred, zero_division=0)
#         prec = precision_score(y_test[col], y_pred, zero_division=0)
#         rec  = recall_score(y_test[col], y_pred, zero_division=0)
#         print(f"{name:<22} — Acc: {acc:.4f} | F1: {f1:.4f} | "
#               f"Precision: {prec:.4f} | Recall: {rec:.4f}")

#         # Save model
#         key_map = {"LogisticRegression":"logreg","RandomForest":"rf",
#                    "XGBoost":"xgb","MLP_NeuralNetwork":"mlp"}
#         joblib.dump(model, f"models/{col}_{key_map[name]}.pkl")

#         # Store metrics
#         all_metrics[col][name] = {
#             "accuracy": round(acc, 4), "f1": round(f1, 4),
#             "precision": round(prec, 4), "recall": round(rec, 4)
#         }

# print("\n✅ All classification models trained and saved.")

# # ── GLUCOSE REGRESSION ─────────────────────────────────────────────────────
# print(f"\n{'='*50}")
# print("  Training Glucose Regression Models")
# print(f"{'='*50}")

# glucose_drop  = ["Glucose_level", "hypertension", "cardiovascular", "kidney"]
# X_glucose_raw = df.drop(columns=glucose_drop)
# y_glucose     = df["Glucose_level"]

# X_train_g_raw, X_test_g_raw, y_train_g, y_test_g = train_test_split(
#     X_glucose_raw, y_glucose, test_size=0.2, random_state=42)

# scaler_glucose = StandardScaler()
# X_train_g = pd.DataFrame(scaler_glucose.fit_transform(X_train_g_raw), columns=X_train_g_raw.columns)
# X_test_g  = pd.DataFrame(scaler_glucose.transform(X_test_g_raw),      columns=X_test_g_raw.columns)

# all_metrics["Glucose_Regression"] = {}

# for name, model in [
#     ("LinearRegression", LinearRegression()),
#     ("MLP_NeuralNetwork", MLPRegressor(
#         hidden_layer_sizes=(128,64,32), activation="relu", solver="adam",
#         alpha=0.001, batch_size=32, learning_rate="adaptive", max_iter=300,
#         early_stopping=True, validation_fraction=0.1, n_iter_no_change=15,
#         random_state=42, verbose=False)),
# ]:
#     model.fit(X_train_g, y_train_g)
#     y_pred_g = model.predict(X_test_g)
#     mae = mean_absolute_error(y_test_g, y_pred_g)
#     r2  = r2_score(y_test_g, y_pred_g)
#     print(f"{name:<22} — MAE: {mae:.4f} | R²: {r2:.4f}")
#     if name == "LinearRegression":
#         joblib.dump(model, "models/glucose_regression.pkl")
#         joblib.dump(scaler_glucose, "models/glucose_scaler.pkl")
#     else:
#         joblib.dump(model, "models/glucose_mlp.pkl")
#     all_metrics["Glucose_Regression"][name] = {
#         "MAE": round(mae, 4), "R2": round(r2, 4)
#     }

# # ── SAVE METRICS JSON ──────────────────────────────────────────────────────
# metrics_path = "models/model_metrics.json"
# with open(metrics_path, "w", encoding="utf-8") as f:
#     json.dump(all_metrics, f, indent=2)
# print(f"\n✅ Metrics saved to {metrics_path}")
# print("✅ All models complete!")


# # ═══════════════════════════════════════════════════════════════════════════
# # DEEP LEARNING — TENSORFLOW MLP
# # ═══════════════════════════════════════════════════════════════════════════
# print(f"\n{'='*50}")
# print("  Training TensorFlow MLP Models")
# print(f"{'='*50}")

# try:
#     import tensorflow as tf
#     import keras
#     from keras import layers
#     import numpy as np

#     tf.random.set_seed(42)

#     for col in disease_targets:
#         print(f"\n--- TF MLP: {col} ---")
#         y_train_col = y_train[col].values
#         y_test_col  = y_test[col].values

#         # Build model
#         model_tf = keras.Sequential([
#             keras.layers.Input(shape=(X_train.shape[1],)),
#             keras.layers.Dense(128, activation="relu"),
#             keras.layers.BatchNormalization(),
#             keras.layers.Dropout(0.3),
#             keras.layers.Dense(64, activation="relu"),
#             keras.layers.BatchNormalization(),
#             keras.layers.Dropout(0.2),
#             keras.layers.Dense(32, activation="relu"),
#             keras.layers.Dense(1, activation="sigmoid")
#         ])
#         model_tf.compile(
#             optimizer=keras.optimizers.Adam(0.001),
#             loss="binary_crossentropy",
#             metrics=["accuracy"]
#         )

#         early_stop = keras.callbacks.EarlyStopping(
#             monitor="val_loss", patience=10, restore_best_weights=True)

#         model_tf.fit(
#             X_train.values, y_train_col,
#             validation_split=0.1,
#             epochs=100, batch_size=32,
#             callbacks=[early_stop],
#             verbose=0
#         )

#         y_pred_tf = (model_tf.predict(X_test.values, verbose=0) > 0.5).astype(int).flatten()
#         acc  = accuracy_score(y_test_col, y_pred_tf)
#         f1   = f1_score(y_test_col, y_pred_tf, zero_division=0)
#         prec = precision_score(y_test_col, y_pred_tf, zero_division=0)
#         rec  = recall_score(y_test_col, y_pred_tf, zero_division=0)
#         print(f"TF_MLP               — Acc: {acc:.4f} | F1: {f1:.4f} | "
#               f"Precision: {prec:.4f} | Recall: {rec:.4f}")

#         # Save as .keras format
#         model_tf.save(f"models/{col}_tf_mlp.keras")

#         all_metrics[col]["TF_MLP"] = {
#             "accuracy": round(acc,4), "f1": round(f1,4),
#             "precision": round(prec,4), "recall": round(rec,4)
#         }

#     print("\n✅ TensorFlow MLP models saved.")

# except ImportError:
#     print("⚠️ TensorFlow not installed. Run: pip install tensorflow")
# except Exception as e:
#     print(f"⚠️ TensorFlow training failed: {e}")


# # ═══════════════════════════════════════════════════════════════════════════
# # DEEP LEARNING — TABNET (pytorch-tabnet)
# # ═══════════════════════════════════════════════════════════════════════════
# print(f"\n{'='*50}")
# print("  Training TabNet Models")
# print(f"{'='*50}")

# try:
#     from pytorch_tabnet.tab_model import TabNetClassifier
#     import numpy as np

#     for col in disease_targets:
#         print(f"\n--- TabNet: {col} ---")
#         y_train_col = y_train[col].values
#         y_test_col  = y_test[col].values

#         tabnet = TabNetClassifier(
#             n_d=16, n_a=16,
#             n_steps=3,
#             gamma=1.3,
#             n_independent=2, n_shared=2,
#             momentum=0.02,
#             optimizer_fn=__import__('torch').optim.Adam,
#             optimizer_params={"lr": 1e-3},
#             scheduler_fn=__import__('torch').optim.lr_scheduler.StepLR,
#             scheduler_params={"step_size": 10, "gamma": 0.9},
#             mask_type="entmax",
#             verbose=0,
#             seed=42
#         )

#         tabnet.fit(
#             X_train=X_train.values.astype(np.float32),
#             y_train=y_train_col,
#             eval_set=[(X_test.values.astype(np.float32), y_test_col)],
#             patience=15,
#             max_epochs=100,
#             batch_size=256,
#             virtual_batch_size=128,
#             eval_metric=["accuracy"]
#         )

#         y_pred_tn = tabnet.predict(X_test.values.astype(np.float32))
#         acc  = accuracy_score(y_test_col, y_pred_tn)
#         f1   = f1_score(y_test_col, y_pred_tn, zero_division=0)
#         prec = precision_score(y_test_col, y_pred_tn, zero_division=0)
#         rec  = recall_score(y_test_col, y_pred_tn, zero_division=0)
#         print(f"TabNet               — Acc: {acc:.4f} | F1: {f1:.4f} | "
#               f"Precision: {prec:.4f} | Recall: {rec:.4f}")

#         tabnet.save_model(f"models/{col}_tabnet")

#         all_metrics[col]["TabNet"] = {
#             "accuracy": round(acc,4), "f1": round(f1,4),
#             "precision": round(prec,4), "recall": round(rec,4)
#         }

#     print("\n✅ TabNet models saved.")

# except ImportError:
#     print("⚠️ TabNet not installed. Run: pip install pytorch-tabnet")
# except Exception as e:
#     print(f"⚠️ TabNet training failed: {e}")


# # ── UPDATE METRICS WITH NEW MODELS ─────────────────────────────────────────
# with open(metrics_path, "w", encoding="utf-8") as f:
#     json.dump(all_metrics, f, indent=2)
# print(f"\n✅ Updated metrics saved to {metrics_path}")
# print("✅ All training complete!")

# #with shap plots
# import os, json
# import joblib
# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# from sklearn.metrics import (accuracy_score, f1_score, precision_score,
#                               recall_score, mean_absolute_error, r2_score,
#                               roc_curve, auc)
# from sklearn.linear_model import LogisticRegression, LinearRegression
# from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
# from sklearn.neural_network import MLPClassifier, MLPRegressor
# from xgboost import XGBClassifier
# from preprocessing import load_dataset, get_disease_data, get_glucose_data

# import matplotlib
# matplotlib.use("Agg")
# import matplotlib.pyplot as plt
# import shap
# import numpy as np

# os.makedirs("models", exist_ok=True)
# os.makedirs("plots", exist_ok=True)

# df = load_dataset()

# disease_targets = ["Diabetes_Diagnosis", "hypertension", "cardiovascular", "kidney"]
# X_raw = df.drop(columns=disease_targets)
# y     = df[disease_targets]

# X_train_raw, X_test_raw, y_train, y_test = train_test_split(
#     X_raw, y, test_size=0.2, random_state=42)

# scaler  = StandardScaler()
# X_train = pd.DataFrame(scaler.fit_transform(X_train_raw), columns=X_train_raw.columns)
# X_test  = pd.DataFrame(scaler.transform(X_test_raw),      columns=X_test_raw.columns)

# joblib.dump(scaler, "models/scaler.pkl")
# features = X_train.columns.tolist()
# print(f"Features used for training: {features}")

# # ── Save metrics here ──────────────────────────────────────────────────────
# all_metrics = {}

# for col in disease_targets:
#     print(f"\n{'='*50}")
#     print(f"  Training models for: {col}")
#     print(f"{'='*50}")
#     all_metrics[col] = {}

#     for name, model in [
#         ("LogisticRegression",   LogisticRegression(max_iter=500)),
#         ("RandomForest",         RandomForestClassifier(n_estimators=100, random_state=42)),
#         ("GradientBoosting",     GradientBoostingClassifier(n_estimators=100, random_state=42)),
#         ("XGBoost",              XGBClassifier(eval_metric="logloss", random_state=42)),
#         ("MLP_NeuralNetwork",    MLPClassifier(
#             hidden_layer_sizes=(128,64,32), activation="relu", solver="adam",
#             alpha=0.001, batch_size=32, learning_rate="adaptive", max_iter=300,
#             early_stopping=True, validation_fraction=0.1, n_iter_no_change=15,
#             random_state=42, verbose=False)),
#     ]:
#         model.fit(X_train, y_train[col])
#         y_pred = model.predict(X_test)
#         acc  = accuracy_score(y_test[col], y_pred)
#         f1   = f1_score(y_test[col], y_pred, zero_division=0)
#         prec = precision_score(y_test[col], y_pred, zero_division=0)
#         rec  = recall_score(y_test[col], y_pred, zero_division=0)
#         print(f"{name:<22} — Acc: {acc:.4f} | F1: {f1:.4f} | "
#               f"Precision: {prec:.4f} | Recall: {rec:.4f}")

#         key_map = {
#             "LogisticRegression": "logreg",
#             "RandomForest":       "rf",
#             "GradientBoosting":   "gb",
#             "XGBoost":            "xgb",
#             "MLP_NeuralNetwork":  "mlp",
#         }
#         joblib.dump(model, f"models/{col}_{key_map[name]}.pkl")

#         all_metrics[col][name] = {
#             "accuracy":  round(acc,  4),
#             "f1":        round(f1,   4),
#             "precision": round(prec, 4),
#             "recall":    round(rec,  4),
#         }

# print("\n✅ All classification models trained and saved.")

# # ── GLUCOSE REGRESSION ─────────────────────────────────────────────────────
# print(f"\n{'='*50}")
# print("  Training Glucose Regression Models")
# print(f"{'='*50}")

# glucose_drop  = ["Glucose_level", "hypertension", "cardiovascular", "kidney"]
# X_glucose_raw = df.drop(columns=glucose_drop)
# y_glucose     = df["Glucose_level"]

# X_train_g_raw, X_test_g_raw, y_train_g, y_test_g = train_test_split(
#     X_glucose_raw, y_glucose, test_size=0.2, random_state=42)

# scaler_glucose = StandardScaler()
# X_train_g = pd.DataFrame(scaler_glucose.fit_transform(X_train_g_raw), columns=X_train_g_raw.columns)
# X_test_g  = pd.DataFrame(scaler_glucose.transform(X_test_g_raw),      columns=X_test_g_raw.columns)

# all_metrics["Glucose_Regression"] = {}

# for name, model in [
#     ("LinearRegression", LinearRegression()),
#     ("MLP_NeuralNetwork", MLPRegressor(
#         hidden_layer_sizes=(128,64,32), activation="relu", solver="adam",
#         alpha=0.001, batch_size=32, learning_rate="adaptive", max_iter=300,
#         early_stopping=True, validation_fraction=0.1, n_iter_no_change=15,
#         random_state=42, verbose=False)),
# ]:
#     model.fit(X_train_g, y_train_g)
#     y_pred_g = model.predict(X_test_g)
#     mae = mean_absolute_error(y_test_g, y_pred_g)
#     r2  = r2_score(y_test_g, y_pred_g)
#     print(f"{name:<22} — MAE: {mae:.4f} | R²: {r2:.4f}")
#     if name == "LinearRegression":
#         joblib.dump(model, "models/glucose_regression.pkl")
#         joblib.dump(scaler_glucose, "models/glucose_scaler.pkl")
#     else:
#         joblib.dump(model, "models/glucose_mlp.pkl")
#     all_metrics["Glucose_Regression"][name] = {
#         "MAE": round(mae, 4), "R2": round(r2, 4)
#     }

# # ── SAVE METRICS JSON ──────────────────────────────────────────────────────
# metrics_path = "models/model_metrics.json"
# with open(metrics_path, "w", encoding="utf-8") as f:
#     json.dump(all_metrics, f, indent=2)
# print(f"\n✅ Metrics saved to {metrics_path}")
# print("✅ All models complete!")


# # ═══════════════════════════════════════════════════════════════════════════
# # DEEP LEARNING — TENSORFLOW MLP
# # ═══════════════════════════════════════════════════════════════════════════
# print(f"\n{'='*50}")
# print("  Training TensorFlow MLP Models")
# print(f"{'='*50}")

# try:
#     import tensorflow as tf
#     import keras
#     from keras import layers

#     tf.random.set_seed(42)

#     for col in disease_targets:
#         print(f"\n--- TF MLP: {col} ---")
#         y_train_col = y_train[col].values
#         y_test_col  = y_test[col].values

#         model_tf = keras.Sequential([
#             keras.layers.Input(shape=(X_train.shape[1],)),
#             keras.layers.Dense(128, activation="relu"),
#             keras.layers.BatchNormalization(),
#             keras.layers.Dropout(0.3),
#             keras.layers.Dense(64, activation="relu"),
#             keras.layers.BatchNormalization(),
#             keras.layers.Dropout(0.2),
#             keras.layers.Dense(32, activation="relu"),
#             keras.layers.Dense(1, activation="sigmoid")
#         ])
#         model_tf.compile(
#             optimizer=keras.optimizers.Adam(0.001),
#             loss="binary_crossentropy",
#             metrics=["accuracy"]
#         )

#         early_stop = keras.callbacks.EarlyStopping(
#             monitor="val_loss", patience=10, restore_best_weights=True)

#         model_tf.fit(
#             X_train.values, y_train_col,
#             validation_split=0.1,
#             epochs=100, batch_size=32,
#             callbacks=[early_stop],
#             verbose=0
#         )

#         y_pred_tf = (model_tf.predict(X_test.values, verbose=0) > 0.5).astype(int).flatten()
#         acc  = accuracy_score(y_test_col, y_pred_tf)
#         f1   = f1_score(y_test_col, y_pred_tf, zero_division=0)
#         prec = precision_score(y_test_col, y_pred_tf, zero_division=0)
#         rec  = recall_score(y_test_col, y_pred_tf, zero_division=0)
#         print(f"TF_MLP               — Acc: {acc:.4f} | F1: {f1:.4f} | "
#               f"Precision: {prec:.4f} | Recall: {rec:.4f}")

#         model_tf.save(f"models/{col}_tf_mlp.keras")

#         all_metrics[col]["TF_MLP"] = {
#             "accuracy": round(acc,4), "f1": round(f1,4),
#             "precision": round(prec,4), "recall": round(rec,4)
#         }

#     print("\n✅ TensorFlow MLP models saved.")

# except ImportError:
#     print("⚠️ TensorFlow not installed. Run: pip install tensorflow")
# except Exception as e:
#     print(f"⚠️ TensorFlow training failed: {e}")


# # ═══════════════════════════════════════════════════════════════════════════
# # DEEP LEARNING — TABNET
# # ═══════════════════════════════════════════════════════════════════════════
# print(f"\n{'='*50}")
# print("  Training TabNet Models")
# print(f"{'='*50}")

# try:
#     from pytorch_tabnet.tab_model import TabNetClassifier

#     for col in disease_targets:
#         print(f"\n--- TabNet: {col} ---")
#         y_train_col = y_train[col].values
#         y_test_col  = y_test[col].values

#         tabnet = TabNetClassifier(
#             n_d=16, n_a=16,
#             n_steps=3,
#             gamma=1.3,
#             n_independent=2, n_shared=2,
#             momentum=0.02,
#             optimizer_fn=__import__('torch').optim.Adam,
#             optimizer_params={"lr": 1e-3},
#             scheduler_fn=__import__('torch').optim.lr_scheduler.StepLR,
#             scheduler_params={"step_size": 10, "gamma": 0.9},
#             mask_type="entmax",
#             verbose=0,
#             seed=42
#         )

#         tabnet.fit(
#             X_train=X_train.values.astype(np.float32),
#             y_train=y_train_col,
#             eval_set=[(X_test.values.astype(np.float32), y_test_col)],
#             patience=15,
#             max_epochs=100,
#             batch_size=256,
#             virtual_batch_size=128,
#             eval_metric=["accuracy"]
#         )

#         y_pred_tn = tabnet.predict(X_test.values.astype(np.float32))
#         acc  = accuracy_score(y_test_col, y_pred_tn)
#         f1   = f1_score(y_test_col, y_pred_tn, zero_division=0)
#         prec = precision_score(y_test_col, y_pred_tn, zero_division=0)
#         rec  = recall_score(y_test_col, y_pred_tn, zero_division=0)
#         print(f"TabNet               — Acc: {acc:.4f} | F1: {f1:.4f} | "
#               f"Precision: {prec:.4f} | Recall: {rec:.4f}")

#         tabnet.save_model(f"models/{col}_tabnet")

#         all_metrics[col]["TabNet"] = {
#             "accuracy": round(acc,4), "f1": round(f1,4),
#             "precision": round(prec,4), "recall": round(rec,4)
#         }

#     print("\n✅ TabNet models saved.")

# except ImportError:
#     print("⚠️ TabNet not installed. Run: pip install pytorch-tabnet")
# except Exception as e:
#     print(f"⚠️ TabNet training failed: {e}")


# # ── UPDATE METRICS WITH ALL NEW MODELS ────────────────────────────────────
# with open(metrics_path, "w", encoding="utf-8") as f:
#     json.dump(all_metrics, f, indent=2)
# print(f"\n✅ Updated metrics saved to {metrics_path}")


# # ═══════════════════════════════════════════════════════════════════════════
# # ROC CURVES — saved to plots/
# # ═══════════════════════════════════════════════════════════════════════════
# print(f"\n{'='*50}")
# print("  Generating ROC Curves")
# print(f"{'='*50}")

# model_key_map = {
#     "LogisticRegression": "logreg",
#     "RandomForest":       "rf",
#     "GradientBoosting":   "gb",
#     "XGBoost":            "xgb",
#     "MLP_NeuralNetwork":  "mlp",
# }

# for col in disease_targets:
#     fig, ax = plt.subplots(figsize=(9, 6))
#     ax.plot([0, 1], [0, 1], "k--", lw=1.2, label="Random (AUC = 0.50)")

#     for name, file_key in model_key_map.items():
#         model_path = f"models/{col}_{file_key}.pkl"
#         if not os.path.exists(model_path):
#             continue
#         mdl = joblib.load(model_path)
#         try:
#             if hasattr(mdl, "predict_proba"):
#                 y_score = mdl.predict_proba(X_test)[:, 1]
#             else:
#                 y_score = mdl.decision_function(X_test)
#             fpr, tpr, _ = roc_curve(y_test[col], y_score)
#             roc_auc     = auc(fpr, tpr)
#             ax.plot(fpr, tpr, lw=2, label=f"{name} (AUC = {roc_auc:.3f})")
#         except Exception as e:
#             print(f"  ⚠️  ROC skipped for {name}/{col}: {e}")

#     ax.set_title(f"ROC Curve — {col}", fontsize=14, fontweight="bold")
#     ax.set_xlabel("False Positive Rate", fontsize=12)
#     ax.set_ylabel("True Positive Rate", fontsize=12)
#     ax.legend(loc="lower right", fontsize=10)
#     ax.grid(alpha=0.3)
#     fig.tight_layout()
#     save_path = f"plots/roc_{col}.png"
#     fig.savefig(save_path, dpi=150)
#     plt.close(fig)
#     print(f"  ✅ Saved: {save_path}")


# # ═══════════════════════════════════════════════════════════════════════════
# # SHAP PLOTS — saved to plots/
# # ═══════════════════════════════════════════════════════════════════════════
# print(f"\n{'='*50}")
# print("  Generating SHAP Plots")
# print(f"{'='*50}")

# for col in disease_targets:

#     # ── 1. XGBoost SHAP (TreeExplainer) ─────────────────────────────────
#     xgb_path = f"models/{col}_xgb.pkl"
#     if os.path.exists(xgb_path):
#         try:
#             xgb_mdl  = joblib.load(xgb_path)
#             explainer = shap.TreeExplainer(xgb_mdl)
#             shap_vals = explainer(X_test)

#             plt.figure(figsize=(9, 5))
#             shap.plots.bar(shap_vals, show=False)
#             plt.title(f"SHAP Feature Importance (XGBoost) — {col}",
#                       fontsize=13, fontweight="bold")
#             plt.tight_layout()
#             plt.savefig(f"plots/shap_bar_xgb_{col}.png", dpi=150, bbox_inches="tight")
#             plt.close("all")
#             print(f"  ✅ Saved: plots/shap_bar_xgb_{col}.png")

#             plt.figure(figsize=(9, 6))
#             shap.plots.beeswarm(shap_vals, show=False)
#             plt.title(f"SHAP Beeswarm (XGBoost) — {col}",
#                       fontsize=13, fontweight="bold")
#             plt.tight_layout()
#             plt.savefig(f"plots/shap_beeswarm_xgb_{col}.png", dpi=150, bbox_inches="tight")
#             plt.close("all")
#             print(f"  ✅ Saved: plots/shap_beeswarm_xgb_{col}.png")

#         except Exception as e:
#             print(f"  ⚠️  SHAP XGBoost failed for {col}: {e}")

#     # ── 2. Gradient Boosting SHAP (TreeExplainer) ───────────────────────
#     gb_path = f"models/{col}_gb.pkl"
#     if os.path.exists(gb_path):
#         try:
#             gb_mdl   = joblib.load(gb_path)
#             explainer = shap.TreeExplainer(gb_mdl)
#             shap_vals = explainer(X_test)

#             plt.figure(figsize=(9, 5))
#             shap.plots.bar(shap_vals, show=False)
#             plt.title(f"SHAP Feature Importance (GradientBoosting) — {col}",
#                       fontsize=13, fontweight="bold")
#             plt.tight_layout()
#             plt.savefig(f"plots/shap_bar_gb_{col}.png", dpi=150, bbox_inches="tight")
#             plt.close("all")
#             print(f"  ✅ Saved: plots/shap_bar_gb_{col}.png")

#             plt.figure(figsize=(9, 6))
#             shap.plots.beeswarm(shap_vals, show=False)
#             plt.title(f"SHAP Beeswarm (GradientBoosting) — {col}",
#                       fontsize=13, fontweight="bold")
#             plt.tight_layout()
#             plt.savefig(f"plots/shap_beeswarm_gb_{col}.png", dpi=150, bbox_inches="tight")
#             plt.close("all")
#             print(f"  ✅ Saved: plots/shap_beeswarm_gb_{col}.png")

#         except Exception as e:
#             print(f"  ⚠️  SHAP GradientBoosting failed for {col}: {e}")

#     # ── 3. Random Forest SHAP (TreeExplainer) ───────────────────────────
#     rf_path = f"models/{col}_rf.pkl"
#     if os.path.exists(rf_path):
#         try:
#             rf_mdl   = joblib.load(rf_path)
#             explainer = shap.TreeExplainer(rf_mdl)
#             shap_vals = explainer(X_test)
#             sv = shap_vals[:, :, 1] if len(shap_vals.shape) == 3 else shap_vals

#             plt.figure(figsize=(9, 5))
#             shap.plots.bar(sv, show=False)
#             plt.title(f"SHAP Feature Importance (RandomForest) — {col}",
#                       fontsize=13, fontweight="bold")
#             plt.tight_layout()
#             plt.savefig(f"plots/shap_bar_rf_{col}.png", dpi=150, bbox_inches="tight")
#             plt.close("all")
#             print(f"  ✅ Saved: plots/shap_bar_rf_{col}.png")

#             plt.figure(figsize=(9, 6))
#             shap.plots.beeswarm(sv, show=False)
#             plt.title(f"SHAP Beeswarm (RandomForest) — {col}",
#                       fontsize=13, fontweight="bold")
#             plt.tight_layout()
#             plt.savefig(f"plots/shap_beeswarm_rf_{col}.png", dpi=150, bbox_inches="tight")
#             plt.close("all")
#             print(f"  ✅ Saved: plots/shap_beeswarm_rf_{col}.png")

#         except Exception as e:
#             print(f"  ⚠️  SHAP RandomForest failed for {col}: {e}")

#     # ── 4. Logistic Regression SHAP (LinearExplainer) ───────────────────
#     lr_path = f"models/{col}_logreg.pkl"
#     if os.path.exists(lr_path):
#         try:
#             lr_mdl   = joblib.load(lr_path)
#             explainer = shap.LinearExplainer(lr_mdl, X_test)
#             shap_vals = explainer(X_test)

#             plt.figure(figsize=(9, 5))
#             shap.plots.bar(shap_vals, show=False)
#             plt.title(f"SHAP Feature Importance (LogisticRegression) — {col}",
#                       fontsize=13, fontweight="bold")
#             plt.tight_layout()
#             plt.savefig(f"plots/shap_bar_logreg_{col}.png", dpi=150, bbox_inches="tight")
#             plt.close("all")
#             print(f"  ✅ Saved: plots/shap_bar_logreg_{col}.png")

#             plt.figure(figsize=(9, 6))
#             shap.plots.beeswarm(shap_vals, show=False)
#             plt.title(f"SHAP Beeswarm (LogisticRegression) — {col}",
#                       fontsize=13, fontweight="bold")
#             plt.tight_layout()
#             plt.savefig(f"plots/shap_beeswarm_logreg_{col}.png", dpi=150, bbox_inches="tight")
#             plt.close("all")
#             print(f"  ✅ Saved: plots/shap_beeswarm_logreg_{col}.png")

#         except Exception as e:
#             print(f"  ⚠️  SHAP LogisticRegression failed for {col}: {e}")

#     # ── 5. MLP SHAP (KernelExplainer) ───────────────────────────────────
#     mlp_path = f"models/{col}_mlp.pkl"
#     if os.path.exists(mlp_path):
#         try:
#             mlp_mdl    = joblib.load(mlp_path)
#             background = shap.sample(X_test, 100, random_state=42)
#             explainer  = shap.KernelExplainer(
#                 mlp_mdl.predict_proba, background)
#             shap_vals  = explainer.shap_values(
#                 X_test.iloc[:200], nsamples=100)
#             sv = shap_vals[1] if isinstance(shap_vals, list) else shap_vals

#             plt.figure(figsize=(9, 5))
#             shap.summary_plot(
#                 sv, X_test.iloc[:200],
#                 plot_type="bar",
#                 feature_names=features,
#                 show=False,
#             )
#             plt.title(f"SHAP Feature Importance (MLP) — {col}",
#                       fontsize=13, fontweight="bold")
#             plt.tight_layout()
#             plt.savefig(f"plots/shap_bar_mlp_{col}.png", dpi=150, bbox_inches="tight")
#             plt.close("all")
#             print(f"  ✅ Saved: plots/shap_bar_mlp_{col}.png")

#             plt.figure(figsize=(9, 6))
#             shap.summary_plot(
#                 sv, X_test.iloc[:200],
#                 feature_names=features,
#                 show=False,
#             )
#             plt.title(f"SHAP Beeswarm (MLP) — {col}",
#                       fontsize=13, fontweight="bold")
#             plt.tight_layout()
#             plt.savefig(f"plots/shap_beeswarm_mlp_{col}.png", dpi=150, bbox_inches="tight")
#             plt.close("all")
#             print(f"  ✅ Saved: plots/shap_beeswarm_mlp_{col}.png")

#         except Exception as e:
#             print(f"  ⚠️  SHAP MLP failed for {col}: {e}")


# # ── FINAL SUMMARY ──────────────────────────────────────────────────────────
# print(f"\n✅ All plots saved to plots/")
# print("\nPlots folder contents:")
# for f_name in sorted(os.listdir("plots")):
#     print(f"  📊 {f_name}")

# print("\n✅ All training complete!")


import os, json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                              recall_score, mean_absolute_error, r2_score,
                              roc_curve, auc)
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier, MLPRegressor
from xgboost import XGBClassifier
from preprocessing import load_dataset, get_disease_data, get_glucose_data

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import shap
import numpy as np

os.makedirs("models", exist_ok=True)
os.makedirs("plots", exist_ok=True)

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
        ("GradientBoosting",   GradientBoostingClassifier(n_estimators=100, random_state=42)),
        ("XGBoost",            XGBClassifier(
                                   eval_metric="logloss",
                                   random_state=42,
                                   base_score=float(0.5))),
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

        key_map = {
            "LogisticRegression": "logreg",
            "RandomForest":       "rf",
            "GradientBoosting":   "gb",
            "XGBoost":            "xgb",
            "MLP_NeuralNetwork":  "mlp",
        }
        joblib.dump(model, f"models/{col}_{key_map[name]}.pkl")

        all_metrics[col][name] = {
            "accuracy":  round(acc,  4),
            "f1":        round(f1,   4),
            "precision": round(prec, 4),
            "recall":    round(rec,  4),
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

    tf.random.set_seed(42)

    for col in disease_targets:
        print(f"\n--- TF MLP: {col} ---")
        y_train_col = y_train[col].values
        y_test_col  = y_test[col].values

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
# DEEP LEARNING — TABNET
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n{'='*50}")
print("  Training TabNet Models")
print(f"{'='*50}")

try:
    from pytorch_tabnet.tab_model import TabNetClassifier

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


# ── UPDATE METRICS WITH ALL NEW MODELS ────────────────────────────────────
with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(all_metrics, f, indent=2)
print(f"\n✅ Updated metrics saved to {metrics_path}")


# ═══════════════════════════════════════════════════════════════════════════
# ROC CURVES — saved to plots/
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n{'='*50}")
print("  Generating ROC Curves")
print(f"{'='*50}")

model_key_map = {
    "LogisticRegression": "logreg",
    "RandomForest":       "rf",
    "GradientBoosting":   "gb",
    "XGBoost":            "xgb",
    "MLP_NeuralNetwork":  "mlp",
}

for col in disease_targets:
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot([0, 1], [0, 1], "k--", lw=1.2, label="Random (AUC = 0.50)")

    for name, file_key in model_key_map.items():
        model_path = f"models/{col}_{file_key}.pkl"
        if not os.path.exists(model_path):
            continue
        mdl = joblib.load(model_path)
        try:
            if hasattr(mdl, "predict_proba"):
                y_score = mdl.predict_proba(X_test)[:, 1]
            else:
                y_score = mdl.decision_function(X_test)
            fpr, tpr, _ = roc_curve(y_test[col], y_score)
            roc_auc     = auc(fpr, tpr)
            ax.plot(fpr, tpr, lw=2, label=f"{name} (AUC = {roc_auc:.3f})")
        except Exception as e:
            print(f"  ⚠️  ROC skipped for {name}/{col}: {e}")

    ax.set_title(f"ROC Curve — {col}", fontsize=14, fontweight="bold")
    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save_path = f"plots/roc_{col}.png"
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"  ✅ Saved: {save_path}")


# ═══════════════════════════════════════════════════════════════════════════
# SHAP PLOTS — saved to plots/
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n{'='*50}")
print("  Generating SHAP Plots")
print(f"{'='*50}")

def _fix_xgb_base_score(mdl):
    """Force base_score to plain float to avoid XGBoost string-storage bug."""
    try:
        bs = mdl.get_params().get("base_score", 0.5)
        if bs is None or str(bs).startswith("["):
            bs = 0.5
        mdl.set_params(base_score=float(bs))
    except Exception:
        mdl.set_params(base_score=0.5)
    return mdl

for col in disease_targets:

    # ── 1. XGBoost SHAP (TreeExplainer) ─────────────────────────────────
    xgb_path = f"models/{col}_xgb.pkl"
    if os.path.exists(xgb_path):
        try:
            xgb_mdl  = joblib.load(xgb_path)
            xgb_mdl  = _fix_xgb_base_score(xgb_mdl)   # ← fix applied here
            explainer = shap.TreeExplainer(xgb_mdl)
            shap_vals = explainer(X_test)

            plt.figure(figsize=(9, 5))
            shap.plots.bar(shap_vals, show=False)
            plt.title(f"SHAP Feature Importance (XGBoost) — {col}",
                      fontsize=13, fontweight="bold")
            plt.tight_layout()
            plt.savefig(f"plots/shap_bar_xgb_{col}.png", dpi=150, bbox_inches="tight")
            plt.close("all")
            print(f"  ✅ Saved: plots/shap_bar_xgb_{col}.png")

            plt.figure(figsize=(9, 6))
            shap.plots.beeswarm(shap_vals, show=False)
            plt.title(f"SHAP Beeswarm (XGBoost) — {col}",
                      fontsize=13, fontweight="bold")
            plt.tight_layout()
            plt.savefig(f"plots/shap_beeswarm_xgb_{col}.png", dpi=150, bbox_inches="tight")
            plt.close("all")
            print(f"  ✅ Saved: plots/shap_beeswarm_xgb_{col}.png")

        except Exception as e:
            print(f"  ⚠️  SHAP XGBoost failed for {col}: {e}")

    # ── 2. Gradient Boosting SHAP (TreeExplainer) ───────────────────────
    gb_path = f"models/{col}_gb.pkl"
    if os.path.exists(gb_path):
        try:
            gb_mdl   = joblib.load(gb_path)
            explainer = shap.TreeExplainer(gb_mdl)
            shap_vals = explainer(X_test)

            plt.figure(figsize=(9, 5))
            shap.plots.bar(shap_vals, show=False)
            plt.title(f"SHAP Feature Importance (GradientBoosting) — {col}",
                      fontsize=13, fontweight="bold")
            plt.tight_layout()
            plt.savefig(f"plots/shap_bar_gb_{col}.png", dpi=150, bbox_inches="tight")
            plt.close("all")
            print(f"  ✅ Saved: plots/shap_bar_gb_{col}.png")

            plt.figure(figsize=(9, 6))
            shap.plots.beeswarm(shap_vals, show=False)
            plt.title(f"SHAP Beeswarm (GradientBoosting) — {col}",
                      fontsize=13, fontweight="bold")
            plt.tight_layout()
            plt.savefig(f"plots/shap_beeswarm_gb_{col}.png", dpi=150, bbox_inches="tight")
            plt.close("all")
            print(f"  ✅ Saved: plots/shap_beeswarm_gb_{col}.png")

        except Exception as e:
            print(f"  ⚠️  SHAP GradientBoosting failed for {col}: {e}")

    # ── 3. Random Forest SHAP (TreeExplainer) ───────────────────────────
    rf_path = f"models/{col}_rf.pkl"
    if os.path.exists(rf_path):
        try:
            rf_mdl   = joblib.load(rf_path)
            explainer = shap.TreeExplainer(rf_mdl)
            shap_vals = explainer(X_test)
            sv = shap_vals[:, :, 1] if len(shap_vals.shape) == 3 else shap_vals

            plt.figure(figsize=(9, 5))
            shap.plots.bar(sv, show=False)
            plt.title(f"SHAP Feature Importance (RandomForest) — {col}",
                      fontsize=13, fontweight="bold")
            plt.tight_layout()
            plt.savefig(f"plots/shap_bar_rf_{col}.png", dpi=150, bbox_inches="tight")
            plt.close("all")
            print(f"  ✅ Saved: plots/shap_bar_rf_{col}.png")

            plt.figure(figsize=(9, 6))
            shap.plots.beeswarm(sv, show=False)
            plt.title(f"SHAP Beeswarm (RandomForest) — {col}",
                      fontsize=13, fontweight="bold")
            plt.tight_layout()
            plt.savefig(f"plots/shap_beeswarm_rf_{col}.png", dpi=150, bbox_inches="tight")
            plt.close("all")
            print(f"  ✅ Saved: plots/shap_beeswarm_rf_{col}.png")

        except Exception as e:
            print(f"  ⚠️  SHAP RandomForest failed for {col}: {e}")

    # ── 4. Logistic Regression SHAP (LinearExplainer) ───────────────────
    lr_path = f"models/{col}_logreg.pkl"
    if os.path.exists(lr_path):
        try:
            lr_mdl   = joblib.load(lr_path)
            explainer = shap.LinearExplainer(lr_mdl, X_test)
            shap_vals = explainer(X_test)

            plt.figure(figsize=(9, 5))
            shap.plots.bar(shap_vals, show=False)
            plt.title(f"SHAP Feature Importance (LogisticRegression) — {col}",
                      fontsize=13, fontweight="bold")
            plt.tight_layout()
            plt.savefig(f"plots/shap_bar_logreg_{col}.png", dpi=150, bbox_inches="tight")
            plt.close("all")
            print(f"  ✅ Saved: plots/shap_bar_logreg_{col}.png")

            plt.figure(figsize=(9, 6))
            shap.plots.beeswarm(shap_vals, show=False)
            plt.title(f"SHAP Beeswarm (LogisticRegression) — {col}",
                      fontsize=13, fontweight="bold")
            plt.tight_layout()
            plt.savefig(f"plots/shap_beeswarm_logreg_{col}.png", dpi=150, bbox_inches="tight")
            plt.close("all")
            print(f"  ✅ Saved: plots/shap_beeswarm_logreg_{col}.png")

        except Exception as e:
            print(f"  ⚠️  SHAP LogisticRegression failed for {col}: {e}")

    # ── 5. MLP SHAP (KernelExplainer) ───────────────────────────────────
    mlp_path = f"models/{col}_mlp.pkl"
    if os.path.exists(mlp_path):
        try:
            mlp_mdl    = joblib.load(mlp_path)
            background = shap.sample(X_test, 100, random_state=42)
            explainer  = shap.KernelExplainer(
                mlp_mdl.predict_proba, background)
            shap_vals  = explainer.shap_values(
                X_test.iloc[:200], nsamples=100)
            sv = shap_vals[1] if isinstance(shap_vals, list) else shap_vals

            plt.figure(figsize=(9, 5))
            shap.summary_plot(
                sv, X_test.iloc[:200],
                plot_type="bar",
                feature_names=features,
                show=False,
            )
            plt.title(f"SHAP Feature Importance (MLP) — {col}",
                      fontsize=13, fontweight="bold")
            plt.tight_layout()
            plt.savefig(f"plots/shap_bar_mlp_{col}.png", dpi=150, bbox_inches="tight")
            plt.close("all")
            print(f"  ✅ Saved: plots/shap_bar_mlp_{col}.png")

            plt.figure(figsize=(9, 6))
            shap.summary_plot(
                sv, X_test.iloc[:200],
                feature_names=features,
                show=False,
            )
            plt.title(f"SHAP Beeswarm (MLP) — {col}",
                      fontsize=13, fontweight="bold")
            plt.tight_layout()
            plt.savefig(f"plots/shap_beeswarm_mlp_{col}.png", dpi=150, bbox_inches="tight")
            plt.close("all")
            print(f"  ✅ Saved: plots/shap_beeswarm_mlp_{col}.png")

        except Exception as e:
            print(f"  ⚠️  SHAP MLP failed for {col}: {e}")


# ── FINAL SUMMARY ──────────────────────────────────────────────────────────
print(f"\n✅ All plots saved to plots/")
print("\nPlots folder contents:")
for f_name in sorted(os.listdir("plots")):
    print(f"  📊 {f_name}")

print("\n✅ All training complete!")