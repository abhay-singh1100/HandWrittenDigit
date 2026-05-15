"""
Generate a confusion matrix and classification report from the trained CNN model.
Saves the confusion matrix heatmap as an image for the research paper.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tensorflow import keras
from sklearn.metrics import confusion_matrix, classification_report

# ─── Configuration ───────────────────────────────────────────────────────────

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "digit_cnn_model.keras")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "sample_images")


def main():
    print("[INFO] Loading MNIST test data ...")
    (_, _), (x_test, y_test) = keras.datasets.mnist.load_data()

    # Preprocess
    x_test = x_test.reshape(-1, 28, 28, 1).astype("float32") / 255.0

    print(f"[INFO] Loading model from {MODEL_PATH} ...")
    model = keras.models.load_model(MODEL_PATH)

    print("[INFO] Generating predictions on 10,000 test images ...")
    y_pred_proba = model.predict(x_test, verbose=0)
    y_pred = np.argmax(y_pred_proba, axis=1)

    # ─── Confusion Matrix ────────────────────────────────────────────────
    cm = confusion_matrix(y_test, y_pred)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=range(10),
        yticklabels=range(10),
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "Count"},
        ax=ax,
    )
    ax.set_xlabel("Predicted Label", fontsize=13, fontweight="bold")
    ax.set_ylabel("True Label", fontsize=13, fontweight="bold")
    ax.set_title("Confusion Matrix — CNN on MNIST Test Set", fontsize=15, fontweight="bold")
    plt.tight_layout()

    cm_path = os.path.join(OUTPUT_DIR, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=150)
    plt.close()
    print(f"[INFO] Confusion matrix saved to {cm_path}")

    # ─── Classification Report ───────────────────────────────────────────
    report = classification_report(y_test, y_pred, digits=4)
    print(f"\n{'='*60}")
    print("  CLASSIFICATION REPORT (per-class precision/recall/F1)")
    print(f"{'='*60}")
    print(report)

    # Save report to text file
    report_path = os.path.join(OUTPUT_DIR, "classification_report.txt")
    with open(report_path, "w") as f:
        f.write("Classification Report — CNN on MNIST Test Set\n")
        f.write("=" * 55 + "\n\n")
        f.write(report)
    print(f"[INFO] Classification report saved to {report_path}")

    # ─── Per-class accuracy bar chart ────────────────────────────────────
    per_class_acc = cm.diagonal() / cm.sum(axis=1)

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = plt.cm.Blues(np.linspace(0.4, 0.85, 10))
    bars = ax.bar(range(10), per_class_acc * 100, color=colors, edgecolor="white", linewidth=1.5)
    ax.set_xlabel("Digit Class", fontsize=13, fontweight="bold")
    ax.set_ylabel("Accuracy (%)", fontsize=13, fontweight="bold")
    ax.set_title("Per-Class Accuracy on MNIST Test Set", fontsize=15, fontweight="bold")
    ax.set_xticks(range(10))
    ax.set_ylim(95, 100.5)
    ax.grid(axis="y", alpha=0.3)

    # Add value labels on bars
    for bar, acc in zip(bars, per_class_acc):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                f"{acc*100:.2f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    acc_path = os.path.join(OUTPUT_DIR, "per_class_accuracy.png")
    plt.savefig(acc_path, dpi=150)
    plt.close()
    print(f"[INFO] Per-class accuracy chart saved to {acc_path}")

    print("\n[DONE] All evaluation artifacts generated.\n")


if __name__ == "__main__":
    main()
