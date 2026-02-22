# 📚 VIVA QUESTIONS & ANSWERS (Quick Version)

## Easy Level

**Q1: What is pneumonia?**
A: Lung infection that fills air sacs with pus/fluid. Can be viral, bacterial, or fungal.

**Q2: Why detect pneumonia early?**
A: Faster treatment, better outcomes, prevents complications, saves lives.

**Q3: What are chest X-rays?**
A: Medical images showing lungs. Dark areas = normal (air), white areas = infection/fluid.

**Q4: Why use AI instead of manual diagnosis?**
A: Faster (seconds vs minutes), consistent, 24/7 available, reduces doctor workload.

**Q5: What is machine learning?**
A: Computers learn patterns from data automatically (not explicitly programmed).

---

## Medium Level

**Q6: Explain your project workflow.**
A: Upload X-ray → Preprocess → Extract features (EfficientNetB0) → Classify (SVM) → Grad-CAM heatmap → Generate PDF report.

**Q7: Why EfficientNetB0?**
A: Pre-trained (ImageNet), lightweight, fast, 90%+ accurate, good for transfer learning.

**Q8: What is transfer learning?**
A: Use pre-trained model knowledge for new task. Saves time/data vs training from scratch.

**Q9: Why SVM instead of neural network?**
A: Works with limited data (5K images), fast, less overfitting, good for binary classification.

**Q10: What is Grad-CAM?**
A: Shows which image regions influenced prediction. Red = important areas. Explains AI decisions.

---

## Hard Level

**Q11: Image preprocessing steps?**
A: 
1. Read grayscale
2. Resize to 224×224 
3. Normalize to 0-1
4. Add dimensions for batch processing

**Q12: What do 1280 features represent?**
A: Learned patterns like edges, textures, shapes that EfficientNetB0 extracts. Each feature detects different patterns.

**Q13: Why RBF kernel for SVM?**
A: Handles non-linear patterns. Medical data is complex, RBF fits better than linear.

**Q14: How is training done?**
A: 
1. Load 5216 images
2. Extract features → (5216, 1280) matrix
3. Train SVM on features
4. Evaluate on 624 test images
5. Result: ~92% accuracy

**Q15: Prediction pipeline?**
A: Preprocess → Extract features → SVM predict → Grad-CAM → Create heatmap → Generate PDF.

---

## Project-Specific

**Q16: What challenges did you face?**
A: Imbalanced data, variable image sizes, limited training data, memory constraints, model serialization.

**Q17: How to improve?**
A: Data augmentation, ensemble methods, multi-class (pneumonia types), attention mechanisms, 3D analysis.

**Q18: Important metrics for medical AI?**
A: Sensitivity (catch pneumonia), specificity (avoid false alarms), precision, F1-score.

**Q19: Why Streamlit?**
A: Easy ML prototyping, no HTML/CSS needed, fast deployment, perfect for demos.

**Q20: Ethical concerns?**
A: Privacy (HIPAA), fairness (avoid bias), transparency (explainability), human-in-loop (doctor decides).

---

**Remember**: Focus on understanding concepts, not just memorizing answers! 🎓
