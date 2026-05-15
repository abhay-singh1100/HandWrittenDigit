"""
=============================================================================
  Handwritten Digit Recognition — FAST BALANCED CNN (v4-final)
  ─────────────────────────────────────────────────────────────
  Fix: removed keras augmentation layers (they ran on val set too,
       causing val_loss explosion). Using ImageDataGenerator instead
       (train-only augmentation, correct behaviour).

  Goals:
    ✓ ~5-8 min on CPU
    ✓ Balanced for ALL 10 digits
    ✓ ~99% test accuracy
=============================================================================
"""

import os, warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"]  = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"]  = "-1"
warnings.filterwarnings("ignore")

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers  # type: ignore
from tensorflow.keras.preprocessing.image import ImageDataGenerator  # type: ignore
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import logging
logging.getLogger("tensorflow").setLevel(logging.ERROR)

# ─── Config ──────────────────────────────────────────────────────────────────
EPOCHS = 15
BATCH  = 256
L2     = 1e-4

MODEL_DIR  = os.path.join(os.path.dirname(__file__), "model")
MODEL_PATH = os.path.join(MODEL_DIR, "digit_cnn_model.keras")
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), "sample_images"), exist_ok=True)


# ─── 1. Load & preprocess ────────────────────────────────────────────────────
def load_and_prep():
    (x_tr, y_tr), (x_te, y_te) = keras.datasets.mnist.load_data()
    x_tr = x_tr.reshape(-1, 28, 28, 1).astype("float32") / 255.0
    x_te = x_te.reshape(-1, 28, 28, 1).astype("float32") / 255.0
    y_tr_cat = keras.utils.to_categorical(y_tr, 10)
    y_te_cat = keras.utils.to_categorical(y_te, 10)
    print(f"[INFO] Train: {x_tr.shape[0]}  Test: {x_te.shape[0]}")
    return x_tr, y_tr, y_tr_cat, x_te, y_te, y_te_cat


# ─── 2. Balanced class weights (max 1.3× — no extreme bias) ──────────────────
def balanced_weights(y_int):
    counts = np.bincount(y_int, minlength=10).astype(float)
    total  = counts.sum()
    w = {d: min(total / (10 * counts[d]), 1.3) for d in range(10)}
    print("[INFO] Class weights:", {d: f"{v:.3f}" for d, v in w.items()})
    return w


# ─── 3. Compact CNN (no augmentation layers inside model) ────────────────────
def build_model():
    reg = regularizers.l2(L2)
    inp = layers.Input(shape=(28, 28, 1))

    # Block 1 — 32 filters
    x = layers.Conv2D(32, 3, padding="same", kernel_regularizer=reg)(inp)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.Conv2D(32, 3, padding="same", kernel_regularizer=reg)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Dropout(0.20)(x)

    # Block 2 — 64 filters
    x = layers.Conv2D(64, 3, padding="same", kernel_regularizer=reg)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.Conv2D(64, 3, padding="same", kernel_regularizer=reg)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Dropout(0.25)(x)

    # Head
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(128, kernel_regularizer=reg)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.Dropout(0.35)(x)
    out = layers.Dense(10, activation="softmax")(x)

    model = keras.Model(inp, out, name="DigitCNN_v4_final")
    model.compile(
        loss=keras.losses.CategoricalCrossentropy(label_smoothing=0.05),
        optimizer=keras.optimizers.Adam(1e-3),
        metrics=["accuracy"],
    )
    model.summary()
    return model


# ─── 4. Train with ImageDataGenerator (train-only augmentation) ──────────────
def train(model, x_tr, y_tr_cat, weights):
    # Split validation manually so generator only sees training data
    n_val   = int(len(x_tr) * 0.10)
    x_val, y_val = x_tr[:n_val], y_tr_cat[:n_val]
    x_fit, y_fit = x_tr[n_val:], y_tr_cat[n_val:]

    # Augmentation applied ONLY to training data
    datagen = ImageDataGenerator(
        rotation_range=8,
        width_shift_range=0.08,
        height_shift_range=0.08,
        zoom_range=0.08,
    )
    datagen.fit(x_fit)

    steps = len(x_fit) // BATCH

    # Build sample_weight array from class_weight dict
    y_int   = np.argmax(y_fit, axis=1)
    s_weight = np.array([weights[d] for d in y_int], dtype="float32")

    cbs = [
        keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=5,
            restore_best_weights=True, verbose=1,
        ),
        keras.callbacks.ModelCheckpoint(
            MODEL_PATH, monitor="val_accuracy",
            save_best_only=True, verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5,
            patience=3, min_lr=1e-6, verbose=1,
        ),
    ]

    return model.fit(
        datagen.flow(x_fit, y_fit, batch_size=BATCH,
                     sample_weight=s_weight),
        steps_per_epoch=steps,
        epochs=EPOCHS,
        validation_data=(x_val, y_val),
        callbacks=cbs,
        verbose=1,
    )


# ─── 5. Evaluate ─────────────────────────────────────────────────────────────
def evaluate(model, x_te, y_te_int, y_te_cat):
    probs  = model.predict(x_te, verbose=0)
    y_pred = np.argmax(probs, axis=1)   # pure softmax — NO hacks

    loss, acc = model.evaluate(x_te, y_te_cat, verbose=0)
    print(f"\n{'='*55}")
    print(f"  Test Loss     : {loss:.4f}")
    print(f"  Test Accuracy : {acc*100:.2f}%")
    print(f"{'='*55}\n")
    print(classification_report(y_te_int, y_pred, digits=4))

    cm = confusion_matrix(y_te_int, y_pred)
    print("── Per-digit accuracy ──")
    for d in range(10):
        c, t = cm[d, d], cm[d].sum()
        err  = {j: cm[d, j] for j in range(10) if j != d and cm[d, j] > 0}
        print(f"  Digit {d}: {c}/{t} ({c/t*100:.2f}%)  errors->{err}")

    plt.figure(figsize=(9, 7))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=range(10), yticklabels=range(10))
    plt.title("Confusion Matrix — v4-final (Balanced)"); plt.tight_layout()
    out = os.path.join(os.path.dirname(__file__), "sample_images", "confusion_matrix.png")
    plt.savefig(out, dpi=110); plt.close()
    print(f"[INFO] Confusion matrix -> {out}")

    model.save(MODEL_PATH)
    print(f"[INFO] Model saved -> {MODEL_PATH}")


# ─── 6. Plot ─────────────────────────────────────────────────────────────────
def plot(hist):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4))
    a1.plot(hist.history["accuracy"],     label="Train")
    a1.plot(hist.history["val_accuracy"], label="Val")
    a1.set_title("Accuracy"); a1.legend(); a1.grid(alpha=0.3)
    a2.plot(hist.history["loss"],     label="Train")
    a2.plot(hist.history["val_loss"], label="Val")
    a2.set_title("Loss"); a2.legend(); a2.grid(alpha=0.3)
    plt.tight_layout()
    out = os.path.join(os.path.dirname(__file__), "sample_images", "training_curves.png")
    plt.savefig(out, dpi=110); plt.close()
    print(f"[INFO] Curves -> {out}")


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*55)
    print("  DIGIT CNN v4-final — BALANCED | ~5-8 min on CPU")
    print("="*55 + "\n")

    x_tr, y_tr, y_tr_cat, x_te, y_te, y_te_cat = load_and_prep()
    weights = balanced_weights(y_tr)
    model   = build_model()
    hist    = train(model, x_tr, y_tr_cat, weights)
    plot(hist)
    evaluate(model, x_te, y_te, y_te_cat)
    print("\n[DONE] Training complete.")
