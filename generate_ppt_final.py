"""
Part 2: Slides 8-14 (Results, Conclusion, References, Thank You)
Run this file directly: python generate_ppt_final.py
"""
from generate_ppt_v3 import *   # import helpers + build() from part1

def build_part2(prs, _ref=None):
    ref = prs.slides[2]   # re-acquire live slide object

    # ═══ SLIDE 8 — RESULTS: TRAINING PERFORMANCE ═══════════════════
    s8=new_slide(prs,ref)
    hdr(s8,"Results — Training Performance",1800000,80000,5500000)
    line(s8,1800000,680000,5500000)

    sec(s8,"Training Curve Observations",200000,780000,4300000)
    bullets(s8,[
        "Epoch 1:  Train acc 95.4%  |  Val acc 98.7%  (fast initial learning)",
        "Epoch 3:  Train acc 98.1%  |  Val acc 99.0%  (steady improvement)",
        "Epoch 5:  Train acc 98.7%  |  Val acc 99.1%  (validation plateau begins)",
        "Epoch 9:  Train acc 99.3%  |  Val acc 99.2%  (EarlyStopping triggered)",
        "Train–Val gap remained < 0.5% throughout all epochs",
        "Loss decreased monotonically — no divergence or instability",
        "ReduceLROnPlateau halved LR at epoch 7 for final convergence",
    ],200000,1100000,4300000,2200000,fs=11)

    sec(s8,"What Training Curves Tell Us",200000,3450000,4300000)
    bullets(s8,[
        "No overfitting: training & validation curves track closely",
        "Dropout (20%, 25%, 35%) prevented co-adaptation of neurons",
        "BatchNormalization stabilised gradient flow each epoch",
        "EarlyStopping saved ~6 unnecessary epochs of compute",
        "Fast convergence validates choice of Adam over SGD",
    ],200000,3780000,4300000,1600000,fs=11)

    # Training curves image right side
    add_img(s8,"training_curves.png",4650000,780000,4200000)
    tb(s8,4650000,3200000,4200000,250000,
       "Fig. 1 — Accuracy & Loss curves across 9 epochs",
       FB,9,C_DGRAY,italic=True,align=PP_ALIGN.CENTER)

    tbl(s8,[
        ["Epoch","Train Acc","Val Acc","Train Loss","Val Loss"],
        ["1","95.4%","98.7%","0.1580","0.0521"],
        ["3","98.1%","99.0%","0.0720","0.0390"],
        ["5","98.7%","99.1%","0.0510","0.0340"],
        ["7","99.1%","99.2%","0.0380","0.0315"],
        ["9*","99.3%","99.2%","0.0290","0.0304"],
    ],4650000,3500000,4200000,1400000)
    tb(s8,4650000,4950000,4200000,200000,
       "* EarlyStopping triggered at Epoch 9 (patience=5)",
       FB,9,C_HL,bold=True,align=PP_ALIGN.CENTER)

    # ═══ SLIDE 9 — RESULTS: TEST ACCURACY & METRICS ════════════════
    s9=new_slide(prs,ref)
    hdr(s9,"Results — Test Set Evaluation",2000000,80000,5100000)
    line(s9,2000000,680000,5100000)

    # Hero metrics
    metrics=[
        ("98.91%","Test Accuracy"),
        ("0.0304","Test Loss"),
        ("1.09%","Error Rate"),
        ("109 / 10,000","Misclassified"),
    ]
    mx=600000
    for val,lbl in metrics:
        s=s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                               Emu(mx),Emu(800000),Emu(1950000),Emu(800000))
        s.fill.solid(); s.fill.fore_color.rgb=C_THEAD
        s.line.color.rgb=C_WHITE
        tf2=s.text_frame; tf2.word_wrap=True
        p2=tf2.paragraphs[0]; p2.alignment=PP_ALIGN.CENTER
        r2=p2.add_run(); r2.text=val
        r2.font.name=FT; r2.font.size=Pt(20)
        r2.font.color.rgb=C_WHITE; r2.font.bold=True
        p3=tf2.add_paragraph(); p3.alignment=PP_ALIGN.CENTER
        r3=p3.add_run(); r3.text=lbl
        r3.font.name=FB; r3.font.size=Pt(10)
        r3.font.color.rgb=RGBColor(0xCC,0xDD,0xFF)
        mx+=2100000

    sec(s9,"Per-Class Classification Report",200000,1780000,8700000,fs=14)
    tbl(s9,[
        ["Digit","Precision","Recall","F1-Score","Support","Per-Class Acc"],
        ["0","0.9888","0.9929","0.9908","980","98.67%"],
        ["1","0.9938","0.9947","0.9943","1,135","99.21%"],
        ["2","0.9799","0.9942","0.9870","1,032","98.35%"],
        ["3","0.9891","0.9911","0.9901","1,010","99.70%"],
        ["4","0.9928","0.9898","0.9913","982","98.88%"],
        ["5","0.9757","0.9910","0.9833","892","98.32%"],
        ["6","0.9947","0.9802","0.9874","958","98.12%"],
        ["7","0.9903","0.9893","0.9898","1,028","99.61%"],
        ["8","0.9938","0.9877","0.9907","974","99.49%"],
        ["9","0.9910","0.9792","0.9850","1,009","98.61%"],
        ["Weighted Avg","0.9891","0.9891","0.9891","10,000","98.91%"],
    ],200000,2080000,8700000,2800000)

    bullets(s9,[
        "Highest recall: Digit 1 (99.47%) — simple straight vertical stroke is unambiguous",
        "Lowest recall:  Digit 9 (97.92%) — top loop confused with digit 4's angled top",
        "Lowest precision: Digit 5 (97.57%) — curved bottom similar to digits 3 and 6",
        "All 10 classes exceed 98.1% per-class accuracy — no single class dominates errors",
    ],200000,5000000,8700000,900000,fs=11)

    # ═══ SLIDE 10 — RESULTS: CONFUSION MATRIX & COMPARISON ═════════
    s10=new_slide(prs,ref)
    hdr(s10,"Results — Confusion Matrix & Comparison",1400000,80000,6300000)
    line(s10,1400000,680000,6300000)

    sec(s10,"Confusion Matrix Analysis",200000,760000,4300000)
    add_img(s10,"confusion_matrix.png",200000,1050000,4100000)
    tb(s10,200000,3750000,4100000,200000,
       "Fig. 2 — Confusion Matrix (10,000 test samples)",
       FB,9,C_DGRAY,italic=True,align=PP_ALIGN.CENTER)

    sec(s10,"Common Error Patterns",200000,4050000,4300000)
    tbl(s10,[
        ["True","Predicted","Count","Reason"],
        ["6","5","9","Similar curved bottom strokes"],
        ["9","4","6","Top loop ≈ angled top of 4"],
        ["9","5","6","Open-top 9 resembles 5"],
        ["0","2","6","Slanted ovals look like 2"],
        ["4","9","5","Closed-top 4 resembles 9"],
        ["7","2","5","Diagonal stroke of 7 ≈ 2"],
    ],200000,4380000,4300000,1500000)

    sec(s10,"Performance vs Baseline Methods",4700000,760000,4200000)
    tbl(s10,[
        ["Method","Test Acc (%)","Params","Notes"],
        ["k-NN (baseline)","96.9","—","No spatial awareness"],
        ["SVM (RBF kernel)","98.6","—","Manual HOG features"],
        ["MLP (784-256-128)","97.8","~236K","Loses spatial info"],
        ["Proposed CNN","98.91","~77K","Auto feature learning"],
        ["LeNet-5","99.2","~60K","More complex training"],
        ["Deep CNN (2010)","99.65","~10M","10M params, GPU needed"],
        ["Ensemble CNNs","99.83","×5M","5 models combined"],
    ],4700000,1100000,4200000,2100000)

    sec(s10,"Key Findings",4700000,3400000,4200000)
    bullets(s10,[
        "Proposed CNN outperforms ALL traditional methods (k-NN, SVM, MLP)",
        "Only 77K parameters vs 236K in MLP — 3× more efficient!",
        "Achieves 98.91% with simple architecture — no GPU required",
        "Misclassifications are mostly genuinely ambiguous handwriting",
        "Balanced class weights eliminated previous digit-8 bias issue",
        "Global Avg Pooling reduces overfitting vs Flatten+Dense",
    ],4700000,3750000,4200000,1800000,fs=11)

    add_img(s10,"per_class_accuracy.png",4700000,5450000,4200000)

    # ═══ SLIDE 11 — WEB APPLICATION DEPLOYMENT ══════════════════════
    s11=new_slide(prs,ref)
    hdr(s11,"Results — Web Application Deployment",1600000,80000,5900000)
    line(s11,1600000,680000,5900000)

    sec(s11,"Streamlit App — DigitAI Pro",200000,780000,4300000)
    bullets(s11,[
        "Built with Streamlit + streamlit-drawable-canvas",
        "4 tabs: Draw Canvas | Upload Image | History | Model Info",
        "Draw tab: 280×280 HTML5 canvas, black bg, white stroke",
        "Real-time prediction: < 5ms per image after model load",
        "Model cached with @st.cache_resource — no reload overhead",
    ],200000,1100000,4300000,1600000,fs=11)

    sec(s11,"Inference Preprocessing Pipeline",200000,2850000,4300000)
    tb(s11,200000,3150000,4300000,1100000,
       "1. Canvas RGBA → grayscale (PIL .convert('L'))\n"
       "2. Detect background polarity → invert if needed\n"
       "3. Fit digit in 20×20 preserving aspect ratio (thumbnail)\n"
       "4. Centre on 28×28 black canvas (4px padding = MNIST style)\n"
       "5. Normalize ÷ 255 → reshape (1,28,28,1)\n"
       "6. model.predict() → softmax probs → argmax = digit",
       FC,10,C_DBLUE)
    tb(s11,200000,4300000,4300000,250000,
       "★ Aspect-ratio preservation fixed '1' misclassified as '8' bug",
       FB,10,C_HL,bold=True)

    sec(s11,"Performance Benchmarks",200000,4650000,4300000)
    tbl(s11,[
        ["Metric","Value"],
        ["Single inference","< 5 ms"],
        ["Model load (first)","~1-2 seconds"],
        ["Model file size","~1.5 MB (.keras)"],
        ["Memory usage","~50 MB (prediction)"],
        ["Training time","~8 min (CPU)"],
    ],200000,4950000,4300000,1200000)

    sec(s11,"Output Display Components",4700000,780000,4200000)
    bullets(s11,[
        "Predicted digit in large gradient circular badge",
        "Confidence % shown below prediction badge",
        "Horizontal bar chart: probability for all 10 classes",
        "Top prediction highlighted in purple-blue gradient",
        "Multi-digit mode: connected-component segmentation",
        "History tab: last 50 predictions, exportable as CSV",
        "Challenge Mode: random digit prompt for practice",
    ],4700000,1100000,4200000,2100000,fs=11)

    sec(s11,"CLI Prediction Utility (predict.py)",4700000,3400000,4200000)
    tb(s11,4700000,3700000,4200000,700000,
       "python predict.py my_digit.png\n\n"
       "Auto-preprocessing:\n"
       "• Grayscale conversion\n"
       "• Background inversion detection\n"
       "• Lanczos resize to 28×28\n"
       "• Text-based probability bar output",
       FC,10,C_DBLUE)

    tbl(s11,[
        ["Deployment Option","Stack","Use Case"],
        ["Streamlit App","Python + Streamlit","Interactive demo"],
        ["CLI Tool","Python + PIL","Batch inference"],
        ["Flask API (future)","Flask + REST","Production backend"],
        ["TFLite (future)","TensorFlow Lite","Mobile/Edge"],
    ],4700000,4500000,4200000,1300000)

    # ═══ SLIDE 12 — CONCLUSION & FUTURE WORK ════════════════════════
    s12=new_slide(prs,ref)
    hdr(s12,"Conclusion & Future Work",2200000,80000,4700000)
    line(s12,2200000,680000,4700000)

    sec(s12,"Summary of Achievements",200000,780000,4300000)
    bullets(s12,[
        "CNN achieves 98.91% test accuracy on 10,000 MNIST test images",
        "All 10 digit classes exceed 98.1% per-class accuracy",
        "Only 77K parameters — lightweight and fast (< 5ms inference)",
        "Outperforms k-NN (96.9%), SVM (98.6%), MLP (97.8%)",
        "End-to-end pipeline: data preprocessing → training → deployment",
        "Working Streamlit web app with real-time canvas drawing",
        "Critical bug fixed: aspect-ratio preservation in preprocessing",
    ],200000,1100000,4300000,2200000,fs=11)

    sec(s12,"Key Technical Contributions",200000,3450000,4300000)
    bullets(s12,[
        "Dual-block CNN with BatchNorm after every Conv layer",
        "GlobalAveragePooling replacing Flatten → 3× fewer params",
        "Train-only augmentation via ImageDataGenerator (val safe)",
        "Balanced class weights (capped 1.3×) for uniform learning",
        "Label smoothing (0.05) for calibrated probability outputs",
        "Reproducible pipeline with EarlyStopping + best-weight restore",
    ],200000,3780000,4300000,1800000,fs=11)

    sec(s12,"Future Work Directions",4700000,780000,4200000)
    fw=[
        ("Multi-Digit Recognition",
         "Segment digit sequences (phone numbers, ZIP codes) "
         "using connected-component labeling or YOLO."),
        ("Data Augmentation++",
         "Elastic distortions, perspective transforms, "
         "and Mixup augmentation for better generalisation."),
        ("Deeper Architectures",
         "ResNet skip connections, SE-Net channel attention, "
         "or Vision Transformer for potential 99.5%+ accuracy."),
        ("TFLite Mobile Deploy",
         "Quantise model (int8) for iOS/Android deployment. "
         "Estimated 75% size reduction, 99%+ accuracy retained."),
        ("Extended Datasets",
         "Train on EMNIST (letters+digits), SVHN (real photos), "
         "and USPS for domain-robust recognition."),
        ("Ensemble Methods",
         "Average predictions from 3-5 models with different seeds. "
         "Typically improves accuracy by 0.1-0.3%."),
    ]
    fy=1100000
    for fname,fdesc in fw:
        tb(s12,4700000,fy,4200000,230000,f"▸ {fname}",FB,11,C_RED,bold=True)
        tb(s12,4700000,fy+230000,4200000,320000,fdesc,FB,9,C_DBLUE)
        fy+=580000

    # ═══ SLIDE 13 — REFERENCES ══════════════════════════════════════
    s13=new_slide(prs,ref)
    hdr(s13,"References",3400000,80000,2300000)
    line(s13,1000000,680000,7100000)

    refs_l=[
        "[1] R.Plamondon & S.N.Srihari, 'Online/offline handwriting recognition,' IEEE TPAMI, 2000.",
        "[2] Y.LeCun, Y.Bengio & G.Hinton, 'Deep learning,' Nature, vol.521, 2015.",
        "[3] I.Goodfellow et al., Deep Learning, MIT Press, 2016.",
        "[4] Y.LeCun et al., 'Gradient-based learning applied to document recognition,' Proc. IEEE, 1998.",
        "[5] A.Krizhevsky et al., 'ImageNet classification with deep CNNs,' NeurIPS, 2012.",
        "[6] N.Srivastava et al., 'Dropout: prevent NNs from overfitting,' JMLR, vol.15, 2014.",
        "[7] S.Ioffe & C.Szegedy, 'Batch Normalization,' Proc. ICML, 2015.",
        "[8] D.P.Kingma & J.Ba, 'Adam: A method for stochastic optimization,' ICLR, 2015.",
    ]
    refs_r=[
        "[9]  K.He et al., 'Deep Residual Learning for Image Recognition,' CVPR, 2016.",
        "[10] D.C.Ciresan et al., 'Deep big simple neural nets for HDR,' Neural Computation, 2010.",
        "[11] L.Wan et al., 'Regularization using DropConnect,' Proc. ICML, 2013.",
        "[12] S.Sabour et al., 'Dynamic routing between capsules,' NeurIPS, 2017.",
        "[13] V.Nair & G.E.Hinton, 'Rectified linear units,' Proc. ICML, 2010.",
        "[14] K.Simonyan & A.Zisserman, 'Very deep CNNs,' Proc. ICLR, 2015.",
        "[15] Streamlit Inc., 'Streamlit: fastest way to build data apps,' streamlit.io, 2023.",
        "[16] F.Chollet et al., 'Keras,' keras.io, 2015.",
    ]
    rtf_l=tb(s13,200000,780000,4300000,4200000,fn=FB,fs=10)
    for ref in refs_l:
        p=rtf_l.add_paragraph(); p.space_before=Pt(4); p.space_after=Pt(2)
        r=p.add_run(); r.text=ref
        r.font.name=FB; r.font.size=Pt(10); r.font.color.rgb=C_BLACK

    rtf_r=tb(s13,4700000,780000,4200000,4200000,fn=FB,fs=10)
    for ref in refs_r:
        p=rtf_r.add_paragraph(); p.space_before=Pt(4); p.space_after=Pt(2)
        r=p.add_run(); r.text=ref
        r.font.name=FB; r.font.size=Pt(10); r.font.color.rgb=C_BLACK

    # ═══ SLIDE 14 — THANK YOU ══════════════════════════════════════
    s14=new_slide(prs,ref)
    tb(s14,0,900000,9144000,900000,"Thank You!",
       FT,48,C_DBLUE,bold=True,align=PP_ALIGN.CENTER)
    tb(s14,0,1800000,9144000,450000,"Questions & Discussion",
       FB,26,C_TITLE,align=PP_ALIGN.CENTER)
    ctf=tb(s14,2000000,2600000,5200000,1800000,fn=FB,fs=14,align=PP_ALIGN.CENTER)
    for txt,bd,sz,cl in [
        ("Abhay Singh",True,18,C_BLACK),
        ("Department of Computer Science",False,13,C_BLACK),
        ("COER University, Roorkee, India",False,13,C_BLACK),
        ("",False,8,C_BLACK),
        ("abhaychauhan5051a@gmail.com",False,13,C_ABLUE),
    ]:
        p=ctf.add_paragraph(); p.alignment=PP_ALIGN.CENTER; p.space_before=Pt(2)
        r=p.add_run(); r.text=txt
        r.font.name=FB; r.font.size=Pt(sz)
        r.font.bold=bd; r.font.color.rgb=cl
    tb(s14,0,4600000,9144000,400000,
       "ICSSCS 2026 — International Conference on Smart & Sustainable Computing Systems",
       FB,12,C_TITLE,bold=True,italic=True,align=PP_ALIGN.CENTER)

    # ── SAVE ─────────────────────────────────────────────────────────
    prs.save(OUT)
    print(f"\n[DONE] Saved: {OUT}")
    n=len(prs.slides)
    print(f"Total slides: {n}")
    names=["Title","Table of Contents","Introduction",
           "Dataset (MNIST)","Methodology: Preprocessing",
           "Methodology: CNN Architecture","Methodology: Training Strategy",
           "Results: Training Curves","Results: Test Accuracy & Per-Class",
           "Results: Confusion Matrix & Comparison",
           "Results: Web App Deployment","Conclusion & Future Work",
           "References","Thank You"]
    for i,nm in enumerate(names[:n],1):
        print(f"  Slide {i:2d}: {nm}")


if __name__ == "__main__":
    prs, _ref = build()
    build_part2(prs)
