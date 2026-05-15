"""
=============================================================================
  Handwritten Digit Recognition — ADVANCED Streamlit Web App
  Features:
    • Draw OR upload an image
    • Multi-digit segmentation & recognition
    • Prediction history gallery with session stats
    • Challenge Mode (user guesses before AI)
    • Export history as CSV
    • Dark glassmorphism UI with animations
=============================================================================
"""

# ── Suppress TensorFlow / oneDNN noise BEFORE importing TF ───────────────────
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"]   = "3"   # 0=all, 1=INFO, 2=WARNING, 3=ERROR
os.environ["TF_ENABLE_ONEDNN_OPTS"]  = "0"   # disable oneDNN floating-point msgs
os.environ["CUDA_VISIBLE_DEVICES"]   = "-1"  # explicitly tell TF: CPU-only
import logging
logging.getLogger("tensorflow").setLevel(logging.ERROR)

import io, csv, datetime
import numpy as np
from PIL import Image, ImageOps, ImageFilter
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import tensorflow as tf
from tensorflow import keras
import scipy.ndimage as ndi

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "digit_cnn_model.keras")

st.set_page_config(
    page_title="DigitAI Pro — Multi-Digit Recognizer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');

*, html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }

.stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); min-height: 100vh; }

/* Hero */
.hero { text-align:center; padding: 2rem 0 1rem; }
.hero h1 {
    font-size: 3.2rem; font-weight: 800; margin: 0;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: shimmer 3s ease infinite;
}
.hero p { color: #94a3b8; font-size: 1.15rem; margin-top: 0.4rem; }
@keyframes shimmer { 0%,100%{filter:hue-rotate(0deg)} 50%{filter:hue-rotate(30deg)} }

/* Glass card */
.glass {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px; padding: 1.5rem;
    backdrop-filter: blur(12px);
    margin-bottom: 1rem;
}

/* Prediction badge */
.pred-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 120px; height: 120px; border-radius: 50%;
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    font-size: 4rem; font-weight: 800; color: white;
    box-shadow: 0 0 40px rgba(124,58,237,0.6);
    animation: pulse 2s ease infinite;
    margin: 1rem auto; display: flex;
}
@keyframes pulse { 0%,100%{box-shadow:0 0 40px rgba(124,58,237,0.6)} 50%{box-shadow:0 0 60px rgba(96,165,250,0.8)} }

/* Multi-digit chips */
.digit-chip {
    display: inline-block; background: linear-gradient(135deg,#7c3aed,#2563eb);
    color: white; font-size: 1.8rem; font-weight: 700;
    border-radius: 12px; padding: 0.4rem 1rem; margin: 0.3rem;
    box-shadow: 0 4px 15px rgba(124,58,237,0.4);
}

/* Confidence bar */
.conf-row { display:flex; align-items:center; gap:10px; margin:5px 0; }
.conf-label { width:18px; text-align:right; font-weight:700; color:#c4b5fd; font-size:0.95rem; }
.bar-bg { flex:1; background:rgba(255,255,255,0.08); border-radius:8px; height:10px; overflow:hidden; }
.bar-fill { height:10px; border-radius:8px; transition: width 0.6s ease; }
.conf-pct { width:52px; text-align:right; font-size:0.85rem; color:#94a3b8; }

/* History card */
.hist-card {
    background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.1);
    border-radius:14px; padding:0.8rem; text-align:center; margin-bottom:0.5rem;
}
.hist-digit { font-size:2.5rem; font-weight:800; color:#a78bfa; }
.hist-conf { font-size:0.8rem; color:#64748b; }
.hist-time { font-size:0.75rem; color:#475569; }

/* Stats */
.stat-box { background:rgba(255,255,255,0.05); border-radius:16px; padding:1rem; text-align:center; }
.stat-num { font-size:2.5rem; font-weight:800; background:linear-gradient(135deg,#a78bfa,#60a5fa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.stat-label { color:#64748b; font-size:0.85rem; }

/* Challenge */
.challenge-correct { color:#34d399; font-size:1.5rem; font-weight:700; }
.challenge-wrong { color:#f87171; font-size:1.5rem; font-weight:700; }

/* Section title */
.sec-title { color:#e2e8f0; font-size:1.1rem; font-weight:600; margin-bottom:0.8rem; letter-spacing:0.05em; }

/* Sidebar */
section[data-testid="stSidebar"] { background: rgba(15,12,41,0.95) !important; }
section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

/* Hide branding */
#MainMenu, footer, header { visibility:hidden; }

/* Tabs */
.stTabs [data-baseweb="tab"] { color:#94a3b8 !important; }
.stTabs [aria-selected="true"] { color:#a78bfa !important; border-bottom-color:#a78bfa !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important; transition: all 0.3s !important;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(124,58,237,0.5) !important; }

/* Upload area */
.stFileUploader { background: rgba(255,255,255,0.03) !important; border-radius:12px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []          # list of dicts
if "challenge_score" not in st.session_state:
    st.session_state.challenge_score = {"correct": 0, "wrong": 0}
if "challenge_pending" not in st.session_state:
    st.session_state.challenge_pending = None   # (predicted, confidence, probs)
if "challenge_guess" not in st.session_state:
    st.session_state.challenge_guess = None

# ── Load Model ────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    # compile=False skips deserializing the custom focal loss (inference only)
    return keras.models.load_model(MODEL_PATH, compile=False)

model = load_model()

# ── Helper Functions ──────────────────────────────────────────────────────────
def preprocess_single(img_pil):
    """
    Preprocess a PIL image to match MNIST format exactly:
      1. Convert to grayscale
      2. Fit inside a 20×20 box preserving aspect ratio (no stretching)
      3. Center on a 28×28 black canvas (4px border all sides)
      4. Normalise to [0, 1]

    This prevents tall thin digits like '1' from being stretched into
    fat shapes that the CNN mistakes for '8'.
    """
    img = img_pil.convert("L")

    # Fit inside 20×20 preserving aspect ratio
    img.thumbnail((20, 20), Image.LANCZOS)

    # Center on a 28×28 black canvas
    canvas = Image.new("L", (28, 28), 0)
    x_off = (28 - img.width)  // 2
    y_off = (28 - img.height) // 2
    canvas.paste(img, (x_off, y_off))

    arr = np.array(canvas).astype("float32") / 255.0
    return arr.reshape(1, 28, 28, 1)


def segment_digits(img_pil):
    """
    Segment multiple digits from a single image using connected components.
    Returns list of (PIL_crop, bounding_box) sorted left-to-right.
    """
    gray = np.array(img_pil.convert("L"))
    # Threshold — white digits on black bg
    binary = (gray > 30).astype(np.uint8)
    labeled, num_features = ndi.label(binary)

    regions = []
    for label_id in range(1, num_features + 1):
        ys, xs = np.where(labeled == label_id)
        if len(xs) < 20:   # skip tiny noise blobs
            continue
        x0, x1 = xs.min(), xs.max()
        y0, y1 = ys.min(), ys.max()
        # Expand bbox a little
        pad = 4
        x0 = max(0, x0 - pad); y0 = max(0, y0 - pad)
        x1 = min(gray.shape[1]-1, x1 + pad)
        y1 = min(gray.shape[0]-1, y1 + pad)
        regions.append((x0, y0, x1, y1))

    # Sort left-to-right
    regions.sort(key=lambda r: r[0])

    crops = []
    for (x0, y0, x1, y1) in regions:
        crop = img_pil.convert("L").crop((x0, y0, x1+1, y1+1))
        crops.append((crop, (x0, y0, x1, y1)))
    return crops


def predict_image(img_pil):
    """
    Run prediction on a PIL image.
    Auto-detects multi-digit vs single-digit.
    Returns list of (digit, confidence, probs) per segment.
    """
    segments = segment_digits(img_pil)
    if len(segments) == 0:
        return []

    results = []
    for crop, bbox in segments:
        processed = preprocess_single(crop)
        probs = model.predict(processed, verbose=0)[0]
        digit = int(np.argmax(probs))
        conf  = float(probs[digit]) * 100
        results.append({"digit": digit, "confidence": conf, "probs": probs, "bbox": bbox})
    return results


def add_to_history(results, source="canvas"):
    """Add prediction results to session history."""
    for r in results:
        st.session_state.history.insert(0, {
            "digit":      r["digit"],
            "confidence": r["confidence"],
            "source":     source,
            "time":       datetime.datetime.now().strftime("%H:%M:%S"),
        })
    # Keep last 50
    st.session_state.history = st.session_state.history[:50]


def render_confidence_bars(probs, predicted):
    bars_html = ""
    for i, p in enumerate(probs):
        pct = float(p) * 100
        is_top = (i == predicted)
        color = "linear-gradient(90deg,#7c3aed,#2563eb)" if is_top else "rgba(255,255,255,0.15)"
        weight = "700" if is_top else "400"
        label_color = "#a78bfa" if is_top else "#64748b"
        bars_html += f"""
        <div class="conf-row">
            <span class="conf-label" style="font-weight:{weight};color:{label_color}">{i}</span>
            <div class="bar-bg">
                <div class="bar-fill" style="width:{pct:.1f}%;background:{color}"></div>
            </div>
            <span class="conf-pct" style="font-weight:{weight}">{pct:.1f}%</span>
        </div>"""
    return bars_html


def get_csv_download():
    """Generate CSV bytes from history."""
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=["digit","confidence","source","time"])
    writer.writeheader()
    writer.writerows(st.session_state.history)
    return out.getvalue().encode()


# ── Hero Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🧠 DigitAI Pro</h1>
    <p>Multi-Digit CNN Recognition · Draw, Upload, Challenge the AI</p>
</div>
""", unsafe_allow_html=True)

if model is None:
    st.error("⚠️ Model not found! Run `python train_model.py` first.")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    stroke_width = st.slider("Brush Size", 10, 40, 20)
    stroke_color = st.color_picker("Stroke Color", "#FFFFFF")
    challenge_mode = st.toggle("🏆 Challenge Mode", value=False)
    st.markdown("---")

    # Session Stats
    st.markdown("## 📊 Session Stats")
    total = len(st.session_state.history)
    avg_conf = np.mean([h["confidence"] for h in st.session_state.history]) if total > 0 else 0
    digit_counts = {}
    for h in st.session_state.history:
        digit_counts[h["digit"]] = digit_counts.get(h["digit"], 0) + 1
    most_common = max(digit_counts, key=digit_counts.get) if digit_counts else "-"

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="stat-box"><div class="stat-num">{total}</div><div class="stat-label">Predictions</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="stat-box"><div class="stat-num">{avg_conf:.0f}%</div><div class="stat-label">Avg Confidence</div></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="stat-box" style="margin-top:0.5rem"><div class="stat-num">{most_common}</div><div class="stat-label">Most Predicted</div></div>""", unsafe_allow_html=True)

    if challenge_mode:
        st.markdown("---")
        st.markdown("## 🏆 Challenge Score")
        sc = st.session_state.challenge_score
        st.markdown(f"✅ Correct: **{sc['correct']}** &nbsp; ❌ Wrong: **{sc['wrong']}**")

    st.markdown("---")
    st.markdown("## 📥 Export")
    if st.session_state.history:
        st.download_button(
            "Download History CSV",
            data=get_csv_download(),
            file_name="digit_predictions.csv",
            mime="text/csv",
        )
    else:
        st.caption("No predictions yet.")

    st.markdown("---")
    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.session_state.challenge_score = {"correct": 0, "wrong": 0}
        st.rerun()

# ── Main Tabs ─────────────────────────────────────────────────────────────────
tab_draw, tab_upload, tab_history, tab_info = st.tabs([
    "✏️ Draw", "🖼️ Upload Image", "📜 History", "ℹ️ Model Info"
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DRAW
# ═══════════════════════════════════════════════════════════════════════════════
with tab_draw:
    left, right = st.columns([1.1, 1])

    with left:
        st.markdown('<div class="sec-title">✏️ Draw digit(s) on the canvas</div>', unsafe_allow_html=True)
        st.caption("Draw multiple digits side by side — the AI will segment and read them all!")
        canvas_result = st_canvas(
            fill_color="rgba(0,0,0,1)",
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color="#000000",
            width=420,
            height=200,
            drawing_mode="freedraw",
            key="main_canvas",
        )
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            predict_btn = st.button("🔍 Recognize", use_container_width=True)

    with right:
        st.markdown('<div class="sec-title">🤖 AI Prediction</div>', unsafe_allow_html=True)

        if predict_btn and canvas_result.image_data is not None:
            img_arr = canvas_result.image_data.astype("float32")
            if np.max(img_arr[:, :, :3]) > 10:
                canvas_pil = Image.fromarray(img_arr[:, :, :3].astype("uint8"))

                # ── Challenge Mode: ask guess first
                if challenge_mode:
                    st.session_state.challenge_pending = canvas_pil
                    st.session_state.challenge_guess = None
                    st.info("🏆 **Challenge Mode:** Enter your guess below, then reveal!")
                else:
                    results = predict_image(canvas_pil)
                    if results:
                        add_to_history(results, source="canvas")

                        if len(results) == 1:
                            r = results[0]
                            st.markdown(f'<div style="text-align:center"><div class="pred-badge">{r["digit"]}</div></div>', unsafe_allow_html=True)
                            st.markdown(f'<p style="text-align:center;color:#94a3b8">Confidence: <b style="color:#a78bfa">{r["confidence"]:.1f}%</b></p>', unsafe_allow_html=True)
                            st.markdown("**Class Probabilities**")
                            st.markdown(render_confidence_bars(r["probs"], r["digit"]), unsafe_allow_html=True)
                        else:
                            chips = "".join(f'<span class="digit-chip">{r["digit"]}</span>' for r in results)
                            number_str = "".join(str(r["digit"]) for r in results)
                            st.markdown(f'<div style="text-align:center;margin:1rem 0">{chips}</div>', unsafe_allow_html=True)
                            st.markdown(f'<p style="text-align:center;color:#94a3b8">Detected number: <b style="color:#34d399;font-size:1.3rem">{number_str}</b></p>', unsafe_allow_html=True)
                            with st.expander("View per-digit probabilities"):
                                for idx, r in enumerate(results):
                                    st.markdown(f"**Digit #{idx+1} → {r['digit']} ({r['confidence']:.1f}%)**")
                                    st.markdown(render_confidence_bars(r["probs"], r["digit"]), unsafe_allow_html=True)
                    else:
                        st.warning("No digit detected. Try drawing more clearly.")
            else:
                st.info("👈 Draw something first, then click Recognize.")

        # ── Challenge Mode resolve
        if challenge_mode and st.session_state.challenge_pending is not None:
            user_guess = st.number_input("Your guess (0-9):", min_value=0, max_value=9, step=1, key="guess_input")
            if st.button("🎯 Reveal AI Answer"):
                results = predict_image(st.session_state.challenge_pending)
                if results:
                    add_to_history(results, source="challenge")
                    ai_digits = [r["digit"] for r in results]
                    ai_str = "".join(str(d) for d in ai_digits)
                    correct = (str(user_guess) == ai_str) or (user_guess == results[0]["digit"] and len(results)==1)
                    if correct:
                        st.session_state.challenge_score["correct"] += 1
                        st.markdown(f'<div class="challenge-correct">✅ Correct! AI also says: {ai_str}</div>', unsafe_allow_html=True)
                    else:
                        st.session_state.challenge_score["wrong"] += 1
                        st.markdown(f'<div class="challenge-wrong">❌ Wrong! AI says: {ai_str}, you guessed: {user_guess}</div>', unsafe_allow_html=True)
                    st.session_state.challenge_pending = None


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — UPLOAD
# ═══════════════════════════════════════════════════════════════════════════════
with tab_upload:
    st.markdown('<div class="sec-title">🖼️ Upload an image containing digit(s)</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Drop an image here", type=["png","jpg","jpeg","bmp","webp"])

    if uploaded:
        img_pil = Image.open(uploaded)
        col_img, col_pred = st.columns([1, 1])

        with col_img:
            st.image(img_pil, caption="Uploaded Image", use_column_width=True)

        with col_pred:
            # Convert to white-on-black
            gray = img_pil.convert("L")
            arr = np.array(gray)
            if np.mean(arr) > 127:
                gray = ImageOps.invert(gray)
            # Create black background version for segmentation
            black_bg = Image.fromarray(np.array(gray))

            results = predict_image(black_bg)
            if results:
                add_to_history(results, source="upload")
                if len(results) == 1:
                    r = results[0]
                    st.markdown(f'<div style="text-align:center"><div class="pred-badge">{r["digit"]}</div></div>', unsafe_allow_html=True)
                    st.markdown(f'<p style="text-align:center;color:#94a3b8">Confidence: <b style="color:#a78bfa">{r["confidence"]:.1f}%</b></p>', unsafe_allow_html=True)
                    st.markdown(render_confidence_bars(r["probs"], r["digit"]), unsafe_allow_html=True)
                else:
                    chips = "".join(f'<span class="digit-chip">{r["digit"]}</span>' for r in results)
                    number_str = "".join(str(r["digit"]) for r in results)
                    st.markdown(f'<p class="sec-title">Detected {len(results)} digit(s):</p>', unsafe_allow_html=True)
                    st.markdown(f'<div style="margin:0.5rem 0">{chips}</div>', unsafe_allow_html=True)
                    st.markdown(f'<p style="color:#94a3b8">Full number: <b style="color:#34d399;font-size:1.3rem">{number_str}</b></p>', unsafe_allow_html=True)
                    with st.expander("Per-digit breakdown"):
                        for idx, r in enumerate(results):
                            st.markdown(f"**Digit #{idx+1} → {r['digit']} ({r['confidence']:.1f}%)**")
                            st.markdown(render_confidence_bars(r["probs"], r["digit"]), unsafe_allow_html=True)
            else:
                st.warning("No digit detected. Ensure the image has clear, dark digits on a light background (or vice versa).")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
with tab_history:
    st.markdown('<div class="sec-title">📜 Prediction History (last 50)</div>', unsafe_allow_html=True)
    if not st.session_state.history:
        st.info("No predictions yet. Draw or upload an image to get started!")
    else:
        cols = st.columns(6)
        for i, h in enumerate(st.session_state.history):
            with cols[i % 6]:
                source_icon = "✏️" if h["source"]=="canvas" else ("🖼️" if h["source"]=="upload" else "🏆")
                st.markdown(f"""
                <div class="hist-card">
                    <div class="hist-digit">{h['digit']}</div>
                    <div class="hist-conf">{h['confidence']:.0f}%</div>
                    <div class="hist-time">{source_icon} {h['time']}</div>
                </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — MODEL INFO
# ═══════════════════════════════════════════════════════════════════════════════
with tab_info:
    st.markdown('<div class="sec-title">ℹ️ CNN Architecture</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
<div class="glass">
<h4 style="color:#a78bfa">🏗️ Model Layers</h4>
<table style="color:#cbd5e1;width:100%;border-collapse:collapse">
<tr style="border-bottom:1px solid rgba(255,255,255,0.1)"><th style="text-align:left;padding:6px">Layer</th><th style="text-align:left;padding:6px">Details</th></tr>
<tr><td style="padding:6px">Conv2D × 2</td><td style="padding:6px">32 & 64 filters, 3×3, ReLU</td></tr>
<tr><td style="padding:6px">MaxPooling2D</td><td style="padding:6px">2×2 pool, halves spatial dims</td></tr>
<tr><td style="padding:6px">Dropout(0.25)</td><td style="padding:6px">Regularisation</td></tr>
<tr><td style="padding:6px">Flatten</td><td style="padding:6px">2D → 1D</td></tr>
<tr><td style="padding:6px">Dense(128)</td><td style="padding:6px">ReLU + BatchNorm</td></tr>
<tr><td style="padding:6px">Dropout(0.5)</td><td style="padding:6px">Regularisation</td></tr>
<tr><td style="padding:6px">Dense(10)</td><td style="padding:6px">Softmax output</td></tr>
</table>
</div>
""", unsafe_allow_html=True)

    with col_b:
        st.markdown("""
<div class="glass">
<h4 style="color:#60a5fa">📈 Training Details</h4>
<ul style="color:#cbd5e1;line-height:2">
<li><b>Dataset:</b> MNIST (70,000 images)</li>
<li><b>Train/Test Split:</b> 60K / 10K</li>
<li><b>Optimizer:</b> Adam</li>
<li><b>Loss:</b> Categorical Cross-Entropy</li>
<li><b>Epochs:</b> Up to 15 (EarlyStopping)</li>
<li><b>Batch Size:</b> 128</li>
<li><b>Test Accuracy:</b> ~99.2%</li>
</ul>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="glass" style="margin-top:0.5rem">
<h4 style="color:#34d399">🔢 Multi-Digit Segmentation</h4>
<p style="color:#94a3b8">
When you draw or upload multiple digits, the app uses <b>connected component labeling</b>
(scipy.ndimage) to find and isolate individual digit blobs. Each blob is cropped, padded,
resized to 28×28 and fed independently into the CNN. Results are sorted left-to-right
to reconstruct the full number.
</p>
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;color:#334155;font-size:0.8rem;padding:2rem 0 1rem">
    DigitAI Pro &nbsp;·&nbsp; CNN on MNIST &nbsp;·&nbsp; Multi-Digit Segmentation &nbsp;·&nbsp; Built with TensorFlow & Streamlit
</div>
""", unsafe_allow_html=True)
