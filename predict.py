"""
=============================================================================
  Handwritten Digit Recognition — Prediction Utility
=============================================================================
  Loads the trained CNN model and predicts the digit in a custom image.

  Usage:
    python predict.py <path_to_image>
    python predict.py sample_images/my_digit.png

  The image can be any size — it will be resized, converted to grayscale,
  and preprocessed to match the MNIST format automatically.
=============================================================================
"""

import sys
import os
import numpy as np
from PIL import Image, ImageOps
import tensorflow as tf
from tensorflow import keras

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "digit_cnn_model.keras")


def preprocess_image(image_path: str) -> np.ndarray:
    """
    Prepare a custom image so it matches MNIST input format (28×28, grayscale,
    white digit on black background, normalised to [0, 1]).

    Steps:
      1. Open the image and convert to grayscale (mode "L").
      2. Invert colours if necessary (MNIST uses white-on-black).
      3. Resize to 28×28 pixels with anti-aliasing.
      4. Normalise pixel values to [0, 1].
      5. Reshape to (1, 28, 28, 1) for model input.
    """
    # Open and convert to grayscale
    img = Image.open(image_path).convert("L")

    # Invert: MNIST has white digits on black background.
    # If the image has a light background, invert it.
    img_array_check = np.array(img)
    if np.mean(img_array_check) > 127:
        img = ImageOps.invert(img)

    # Resize to 28×28
    img = img.resize((28, 28), Image.LANCZOS)

    # Convert to numpy and normalise
    img_array = np.array(img).astype("float32") / 255.0

    # Reshape for model: (1, 28, 28, 1)
    img_array = img_array.reshape(1, 28, 28, 1)
    return img_array


def predict_digit(image_path: str):
    """Load the model and predict the digit in the given image."""
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Trained model not found at {MODEL_PATH}")
        print("        Run 'python train_model.py' first to train the model.")
        sys.exit(1)

    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        sys.exit(1)

    # Load model
    print(f"[INFO] Loading model from {MODEL_PATH} ...")
    model = keras.models.load_model(MODEL_PATH)

    # Preprocess
    processed = preprocess_image(image_path)

    # Predict
    predictions = model.predict(processed, verbose=0)
    predicted_class = np.argmax(predictions[0])
    confidence = predictions[0][predicted_class] * 100

    print(f"\n{'='*45}")
    print(f"  Image           : {image_path}")
    print(f"  Predicted Digit : {predicted_class}")
    print(f"  Confidence      : {confidence:.2f}%")
    print(f"{'='*45}")
    print(f"\n  All class probabilities:")
    for i, prob in enumerate(predictions[0]):
        bar = "█" * int(prob * 30)
        print(f"    {i}: {prob*100:6.2f}%  {bar}")
    print()

    return predicted_class, confidence


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict.py <path_to_image>")
        print("Example: python predict.py sample_images/my_digit.png")
        sys.exit(1)

    predict_digit(sys.argv[1])
