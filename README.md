# ✍️ Handwritten Digit Recognition with CNN

A complete, production-ready **Convolutional Neural Network (CNN)** system that recognises handwritten digits (0–9) using TensorFlow/Keras, trained on the MNIST dataset, with a Streamlit web app for interactive prediction.

---

## 📂 Project Structure

```
HandWrittenDigit/
├── README.md              ← You are here
├── requirements.txt       ← Python dependencies
├── train_model.py         ← CNN training pipeline
├── predict.py             ← CLI prediction for custom images
├── app.py                 ← Streamlit web app (draw & predict)
├── model/
│   └── digit_cnn_model.keras   ← Saved trained model
└── sample_images/
    ├── training_samples.png    ← Generated sample grid
    └── training_curves.png     ← Accuracy/loss plots
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Train the Model

```bash
python train_model.py
```

### 3. Predict on a Custom Image

```bash
python predict.py path/to/your/digit.png
```

### 4. Launch the Web App

```bash
streamlit run app.py
```

---

## 📖 Conceptual Overview

### What is Handwritten Digit Recognition?

Handwritten digit recognition is the ability of a computer to interpret images of digits (0–9) written by hand. It is one of the foundational problems in computer vision and a common entry point for learning deep learning.

**Real-world applications:**
- 📬 Postal mail sorting (ZIP code reading)
- 🏦 Bank cheque processing
- 📋 Form digitisation (tax forms, surveys)
- 📱 On-device handwriting input (phones, tablets)
- 🔐 CAPTCHA systems

### Why CNN Instead of Traditional Neural Networks?

| Feature | Traditional MLP | CNN |
|---|---|---|
| **Input handling** | Flattens image to 1-D (loses spatial info) | Processes 2-D image directly |
| **Parameters** | 28×28×128 = 100K+ for first layer alone | 3×3×32 = 288 params per filter |
| **Spatial awareness** | None — every pixel connected to every neuron | Local connectivity via sliding filters |
| **Translation invariance** | None | Built-in via pooling layers |
| **Feature learning** | Manual feature engineering needed | Automatically learns hierarchical features |

**Key advantages of CNNs:**

1. **Parameter sharing** — The same 3×3 filter slides across the entire image, so the network learns features (edges, curves) once and applies them everywhere.
2. **Spatial hierarchy** — Stacked convolutional layers learn increasingly abstract features: edges → corners → shapes → digit patterns.
3. **Translation invariance** — Pooling layers make the network robust to small shifts in the digit's position.

---

## 📊 The MNIST Dataset

The **Modified National Institute of Standards and Technology (MNIST)** dataset is the standard benchmark for digit recognition.

| Property | Value |
|---|---|
| **Total images** | 70,000 |
| **Training set** | 60,000 |
| **Test set** | 10,000 |
| **Image size** | 28 × 28 pixels |
| **Colour** | Grayscale (1 channel) |
| **Pixel range** | 0 (black) – 255 (white) |
| **Classes** | 10 (digits 0-9) |
| **Format** | White digit on black background |

### Preprocessing Steps

1. **Reshape** — `(60000, 28, 28)` → `(60000, 28, 28, 1)` — add channel dimension for CNN.
2. **Normalise** — Scale from `[0, 255]` to `[0.0, 1.0]` for faster and more stable training.
3. **One-hot encode** — Labels `3` → `[0,0,0,1,0,0,0,0,0,0]` for categorical cross-entropy loss.

---

## 🏗️ CNN Architecture — Detailed Layer Explanation

```
Input: 28×28×1 grayscale image
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ Conv2D(32, 3×3, ReLU)     ← 32 feature maps, learns edges     │
│ Output: 26×26×32                                                │
├─────────────────────────────────────────────────────────────────┤
│ Conv2D(64, 3×3, ReLU)     ← 64 feature maps, learns patterns  │
│ Output: 24×24×64                                                │
├─────────────────────────────────────────────────────────────────┤
│ MaxPooling2D(2×2)         ← Halves spatial dims                │
│ Output: 12×12×64                                                │
├─────────────────────────────────────────────────────────────────┤
│ Dropout(0.25)             ← Regularisation                     │
│ Output: 12×12×64                                                │
├─────────────────────────────────────────────────────────────────┤
│ Flatten()                 ← 12×12×64 = 9216 neurons            │
│ Output: 9216                                                    │
├─────────────────────────────────────────────────────────────────┤
│ Dense(128, ReLU)          ← Fully connected classifier         │
│ Output: 128                                                     │
├─────────────────────────────────────────────────────────────────┤
│ BatchNormalization        ← Stabilises training                 │
│ Output: 128                                                     │
├─────────────────────────────────────────────────────────────────┤
│ Dropout(0.5)              ← Strong regularisation               │
│ Output: 128                                                     │
├─────────────────────────────────────────────────────────────────┤
│ Dense(10, Softmax)        ← Output probabilities for 0-9       │
│ Output: 10                                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Layer-by-Layer Explanation

#### 1. Conv2D(32, kernel_size=3×3, activation=ReLU)
- **What**: Applies 32 learnable 3×3 filters (kernels) across the input image.
- **Why**: Detects low-level features — horizontal edges, vertical edges, corners.
- **Output shape**: `(26, 26, 32)` — reduced by 2 in each spatial dimension due to "valid" padding.
- **ReLU**: `f(x) = max(0, x)` — introduces non-linearity; allows the network to learn complex patterns. Fast to compute, avoids the vanishing gradient problem of sigmoid/tanh.

#### 2. Conv2D(64, kernel_size=3×3, activation=ReLU)
- **What**: 64 filters that process the first layer's output.
- **Why**: Combines low-level features into higher-level patterns (curves, loops, strokes).
- **Output shape**: `(24, 24, 64)`.

#### 3. MaxPooling2D(pool_size=2×2)
- **What**: Slides a 2×2 window over the input and keeps only the maximum value.
- **Why**:
  - **Reduces computation** — halves spatial dimensions (24×24 → 12×12).
  - **Translation invariance** — if a feature shifts by 1 pixel, the max stays the same.
  - **Reduces overfitting** — fewer parameters to learn.

#### 4. Dropout(0.25)
- **What**: During each training step, randomly sets 25% of activations to zero.
- **Why**: Forces the network to learn redundant representations, preventing over-reliance on specific neurons. Disabled during inference.

#### 5. Flatten()
- **What**: Reshapes the 3-D feature map `(12, 12, 64)` into a 1-D vector of 9,216 values.
- **Why**: Dense layers require 1-D input.

#### 6. Dense(128, activation=ReLU)
- **What**: Fully connected layer with 128 neurons.
- **Why**: Learns complex combinations of extracted features to distinguish between digit classes.

#### 7. BatchNormalization
- **What**: Normalises the activations of the previous layer (zero mean, unit variance) within each mini-batch.
- **Why**:
  - **Faster convergence** — allows higher learning rates.
  - **Internal covariate shift** — reduces the shifting distribution of layer inputs during training.
  - **Slight regularisation** — acts as a mild alternative to Dropout.

#### 8. Dropout(0.5)
- **What**: Drops 50% of neurons randomly.
- **Why**: Aggressive regularisation before the output layer to prevent the dense classifier from memorising training data.

#### 9. Dense(10, activation=Softmax)
- **What**: Output layer with 10 neurons (one per digit class).
- **Softmax**: Converts raw logits into a probability distribution that sums to 1.0.
- **Example output**: `[0.01, 0.02, 0.01, 0.85, 0.03, 0.01, 0.02, 0.01, 0.03, 0.01]` → predicted digit is **3** (85% confidence).

---

## 📈 Expected Output & Performance

### Training Output (typical)
```
Epoch 1/15 — accuracy: 0.9650 — val_accuracy: 0.9870
Epoch 2/15 — accuracy: 0.9850 — val_accuracy: 0.9900
...
Epoch 10/15 — accuracy: 0.9935 — val_accuracy: 0.9940
```

### Test Set Evaluation
```
==================================================
  Test Loss     : ~0.0200
  Test Accuracy : ~0.9930  (99.30%)
==================================================
```

### Performance Insights

| Metric | Value |
|---|---|
| **Test accuracy** | ~99.2 – 99.4% |
| **Training time** | ~2-5 minutes (GPU), ~10-15 min (CPU) |
| **Model size** | ~1.5 MB (.keras format) |
| **Parameters** | ~1.2 million |
| **Inference time** | < 5 ms per image |

---

## 🧪 Testing with Custom Images

### Using the CLI

```bash
python predict.py my_digit.png
```

**Tips for best results:**
- Write the digit clearly in the centre of the image.
- Use a **dark background with a white/light digit** (MNIST format).
- Keep thick, clear strokes.
- Square images work best (the script handles resizing).

### Using the Web App

```bash
streamlit run app.py
```

Draw directly on the canvas and see real-time predictions with confidence bars.

---

## 🔧 Possible Improvements

### 1. Data Augmentation
```python
from tensorflow.keras.preprocessing.image import ImageDataGenerator

datagen = ImageDataGenerator(
    rotation_range=10,       # Random rotation ±10°
    width_shift_range=0.1,   # Horizontal shift
    height_shift_range=0.1,  # Vertical shift
    zoom_range=0.1,          # Random zoom
)
model.fit(datagen.flow(x_train, y_train, batch_size=128), epochs=15)
```
**Benefit**: Exposes the model to more variations, improving generalisation.

### 2. Deeper Architecture
```python
model = models.Sequential([
    layers.Conv2D(32, (3,3), activation='relu', input_shape=(28,28,1)),
    layers.BatchNormalization(),
    layers.Conv2D(32, (3,3), activation='relu'),
    layers.MaxPooling2D((2,2)),
    layers.Dropout(0.25),

    layers.Conv2D(64, (3,3), activation='relu'),
    layers.BatchNormalization(),
    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D((2,2)),
    layers.Dropout(0.25),

    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.5),
    layers.Dense(10, activation='softmax'),
])
```
**Benefit**: Learns more complex features; can push accuracy to ~99.5%+.

### 3. Learning Rate Scheduling
```python
lr_scheduler = keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss', factor=0.5, patience=2
)
```
**Benefit**: Reduces the learning rate when progress stalls, enabling finer convergence.

### 4. Ensemble Methods
Train multiple models with different architectures or random seeds and average their predictions. Can improve accuracy by 0.1–0.3%.

---

## 🌍 Real-World Applications

| Application | Description |
|---|---|
| 📬 **Postal sorting** | Automatically read ZIP codes on envelopes |
| 🏦 **Banking** | Process handwritten cheque amounts |
| 📋 **Form digitisation** | Extract handwritten numbers from tax forms, medical records |
| 📱 **Mobile input** | Handwriting recognition on phone/tablet keyboards |
| 🔐 **CAPTCHA** | Recognise distorted digits in security challenges |
| 🏥 **Healthcare** | Read handwritten patient IDs and prescription numbers |
| 🎓 **Education** | Auto-grade numerical answers on exam sheets |
| 🚗 **License plates** | Recognise digits in license plate detection systems |

---

## 🖥️ Deployment Options

### Option 1: Streamlit Web App (Included)
```bash
streamlit run app.py
```
- Zero-config web interface
- Drawing canvas for live prediction
- Confidence visualisation

### Option 2: Flask REST API
```python
from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
from tensorflow import keras

app = Flask(__name__)
model = keras.models.load_model("model/digit_cnn_model.keras")

@app.route("/predict", methods=["POST"])
def predict():
    file = request.files["image"]
    img = Image.open(file).convert("L").resize((28, 28))
    img_array = np.array(img).astype("float32") / 255.0
    img_array = img_array.reshape(1, 28, 28, 1)
    preds = model.predict(img_array, verbose=0)
    return jsonify({
        "digit": int(np.argmax(preds[0])),
        "confidence": float(np.max(preds[0])) * 100
    })

if __name__ == "__main__":
    app.run(debug=True)
```

### Option 3: PyQt5 Desktop GUI
A drawing canvas application where users draw a digit and get instant predictions. See the [predict.py](predict.py) module for the prediction logic — wrap it in a PyQt5 `QMainWindow` with a `QPainter` canvas.

---

## 🎯 Interview-Ready Q&A

### Q: Why use ReLU instead of Sigmoid?
**A:** ReLU (`max(0, x)`) avoids the **vanishing gradient** problem that plagues Sigmoid/Tanh in deep networks. Its gradient is either 0 or 1, enabling efficient backpropagation through many layers. It's also computationally cheaper.

### Q: What is the purpose of MaxPooling?
**A:** MaxPooling serves three goals: (1) **dimensionality reduction** — halves spatial dimensions, reducing computation; (2) **translation invariance** — the output remains similar even if the feature shifts slightly; (3) **regularisation** — reduces the number of parameters.

### Q: Why Softmax for the output layer?
**A:** Softmax converts raw logits into a **probability distribution** (all values in [0,1] summing to 1). This is ideal for multi-class classification — the predicted digit is the class with the highest probability.

### Q: How does Dropout prevent overfitting?
**A:** Dropout randomly zeroes out neurons during training, forcing the network to learn **redundant representations**. No single neuron can dominate, making the model more robust and generalisable.

### Q: Why normalise pixel values to [0, 1]?
**A:** Normalisation ensures all features are on the same scale. Without it, large pixel values (0–255) can cause **exploding gradients** and slow down convergence. It also helps the optimiser find the loss minimum faster.

### Q: What is Batch Normalisation?
**A:** BatchNorm normalises layer inputs to have zero mean and unit variance within each mini-batch. This (1) allows higher learning rates, (2) reduces sensitivity to weight initialisation, and (3) acts as a mild regulariser.

### Q: What is the difference between `valid` and `same` padding?
**A:** 
- **Valid**: No padding. Output size = `(input - kernel + 1)`. Example: 28×28 with 3×3 filter → 26×26.
- **Same**: Zero-pad the input so the output has the **same** spatial dimensions as the input.

### Q: How would you improve this model for production?
**A:** (1) Data augmentation, (2) deeper architecture with residual connections, (3) learning rate scheduling, (4) ensemble of models, (5) test-time augmentation, (6) quantisation for mobile deployment.

---

## 📜 License

This project is for educational purposes. The MNIST dataset is provided by Yann LeCun and is freely available for research.
