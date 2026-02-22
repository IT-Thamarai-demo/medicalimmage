# 🚀 HOW TO RUN THIS PROJECT - STEP BY STEP

## ⚡ SUPER QUICK VERSION (5 minutes)

```bash
# 1. Install Python packages
pip install -r requirements.txt

# 2. Train models on Google Colab (or get pre-trained ones)
# See "DETAILED STEPS" below

# 3. Run the app
streamlit run app.py

# 4. Open browser at: http://localhost:8501
# 5. Upload a chest X-ray image
# 6. See prediction & heatmap
# 7. Download PDF report
```

---

## 📋 DETAILED STEP-BY-STEP GUIDE

### **PHASE 1: SETUP (5-10 minutes)**

#### Step 1: Check Python Installation
```bash
# Open PowerShell/Terminal and run:
python --version

# Should show: Python 3.8 or higher
# If not installed: Download from python.org
```

#### Step 2: Install Dependencies
```bash
# Navigate to project folder
cd c:\Users\Asus\Desktop\medicalimmage

# Install all packages
pip install -r requirements.txt

# Wait for installation (2-3 minutes)
# You should see: "Successfully installed..."
```

**What gets installed:**
- TensorFlow (deep learning)
- scikit-learn (SVM)
- Streamlit (web interface)
- OpenCV (image processing)
- reportlab (PDF generation)

---

### **PHASE 2: TRAIN THE MODEL (1-2 hours)**

#### Step 3: Get Trained Models

**Option A: Train on Google Colab (RECOMMENDED - FREE GPU)**

```
1. Go to: https://colab.research.google.com
2. Create new notebook
3. Click "File" → "Open notebook" → "Upload"
4. Upload: Training_Notebook.ipynb (from your project)
5. Follow notebook instructions:
   - Mount Google Drive
   - Install packages
   - Load chest_xray/ dataset
   - Extract features
   - Train SVM
   - Save models
6. Download trained models:
   - efficient_model.h5
   - svm_model.pkl
7. Save to: c:\Users\Asus\Desktop\medicalimmage\models\
```

**Option B: Use Pre-Trained Models**
```
1. Get pre-trained models from:
   - Hugging Face Model Hub
   - GitHub releases
2. Extract to: models/ folder
```

#### Step 4: Verify Models Are Present
```bash
# Check if models exist
dir models\

# You should see:
# - efficient_model.h5 (40 MB)
# - svm_model.pkl (5 MB)
```

**If models are missing:**
```
❌ App will NOT work
✅ Train on Colab first (see Step 3)
```

---

### **PHASE 3: RUN LOCALLY (2-3 minutes)**

#### Step 5: Start Streamlit App
```bash
# Make sure you're in project folder
cd c:\Users\Asus\Desktop\medicalimmage

# Run the app
streamlit run app.py

# You should see:
# Streamlit app is running on http://localhost:8501
```

#### Step 6: Open in Web Browser
```
1. Open web browser (Chrome, Edge, Firefox, etc.)
2. Go to: http://localhost:8501
3. You should see the app interface
```

#### Step 7: Test the App
```
1. Click "Choose file" button
2. Select a chest X-ray image (JPG or PNG)
3. Wait 2-3 seconds for processing
4. Should see:
   ✓ Prediction: "Pneumonia" or "Normal"
   ✓ Confidence score
   ✓ Original X-ray image
   ✓ Grad-CAM heatmap
   ✓ PDF download button
```

#### Step 8: Download PDF Report
```
1. Click "📥 Download PDF Report"
2. PDF saves to Downloads folder
3. Open and verify report contains:
   ✓ Prediction result
   ✓ Confidence percentage
   ✓ Original X-ray image
   ✓ Grad-CAM heatmap
   ✓ Medical disclaimer
```

---

## 🎯 COMPLETE COMMAND SEQUENCE

### Copy-paste this entire sequence:

```powershell
# Navigate to project
cd c:\Users\Asus\Desktop\medicalimmage

# Install dependencies
pip install -r requirements.txt

# Run app (after training models!)
streamlit run app.py

# Browser will open automatically at http://localhost:8501
```

---

## 📊 WHAT HAPPENS AT EACH STEP

### Step 1: pip install -r requirements.txt
```
Downloads and installs:
├─ TensorFlow (deep learning)
├─ scikit-learn (machine learning)
├─ Streamlit (web framework)
├─ OpenCV (image processing)
├─ reportlab (PDF generation)
└─ Other dependencies

Status: ✓ Takes 2-3 minutes
Result: All packages ready to use
```

### Step 2: Model Training
```
What happens:
├─ Load 5,216 chest X-ray images
├─ Extract 1,280 features per image (EfficientNetB0)
├─ Train SVM classifier (5-10 minutes)
├─ Evaluate on 624 test images
└─ Save models

Result:
├─ efficient_model.h5 (40 MB)
└─ svm_model.pkl (5 MB)

Status: Takes 1-2 hours on Colab GPU
```

### Step 3: streamlit run app.py
```
What happens:
├─ Starts Streamlit server
├─ Loads models (10 seconds)
├─ Creates web interface
├─ Opens browser automatically
└─ Ready for image upload

Status: ✓ Instant (5 seconds)
Result: Web app runs on http://localhost:8501
```

### Step 4: Image Upload & Prediction
```
What happens:
├─ Read user's X-ray image
├─ Preprocess (resize, normalize)
├─ Extract features (2 seconds)
├─ Predict with SVM (0.5 seconds)
├─ Generate Grad-CAM heatmap (0.5 seconds)
└─ Create PDF report (1 second)

Status: Takes 2-3 seconds total
Result: All visualizations displayed
```

---

## ❌ TROUBLESHOOTING

### Problem: "Python not found"
```bash
# Solution:
1. Download Python 3.8+ from python.org
2. Check "Add Python to PATH" during installation
3. Restart PowerShell
4. Try again: python --version
```

### Problem: "ModuleNotFoundError: tensorflow"
```bash
# Solution:
pip install -r requirements.txt
# Wait for all packages to install
```

### Problem: "Models not found"
```bash
# Solution:
1. Train on Google Colab (see Step 3)
2. Download efficient_model.h5 and svm_model.pkl
3. Save to: c:\Users\Asus\Desktop\medicalimmage\models\
4. Check: dir models\ (should show both files)
```

### Problem: "App won't start"
```bash
# Solution:
1. Check Python version: python --version
2. Check packages: pip list | grep streamlit
3. Try installing again: pip install streamlit
4. Restart PowerShell
5. Try again: streamlit run app.py
```

### Problem: "Port 8501 already in use"
```bash
# Solution:
streamlit run app.py --server.port 8502
# App will run on: http://localhost:8502
```

---

## 🔄 TYPICAL WORKFLOW

```
9 AM: Start training on Google Colab
      ↓ (Let it run for 1-2 hours)
11 AM: Download trained models
       ↓
11:15 AM: Place models in models/ folder
          ↓
11:20 AM: Run: streamlit run app.py
          ↓
11:25 AM: Upload test X-ray image
          ↓
11:28 AM: See prediction & heatmap
          ↓
11:30 AM: Download PDF report
          ↓
Done! ✓
```

---

## 📱 TO RUN STREAMLIT APP

### Quick Command
```bash
cd c:\Users\Asus\Desktop\medicalimmage
streamlit run app.py
```

### What You'll See
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://xxx.xxx.x.xxx:8501

  For better performance, install watchdog.
```

### Browser Opens Automatically
- If not, open manually: http://localhost:8501

---

## 🛑 TO STOP THE APP

```bash
# Press Ctrl+C in the terminal

# Or close the terminal
```

---

## 📚 FILE STRUCTURE FOR RUNNING

```
medicalimmage/
├── app.py                    ⭐ RUN THIS FILE
├── requirements.txt          (install from this)
├── chest_xray/               (dataset - already present)
├── models/                   (add trained models here)
│   ├── efficient_model.h5
│   └── svm_model.pkl
└── src/
    ├── data_loader.py
    ├── model.py
    ├── cam.py
    └── pdf_gen.py
```

---

## ⏱️ TIMELINE

```
Activity                    Time        Status
─────────────────────────────────────────────────
1. pip install              2-3 min     ⏳ First time only
2. Google Colab training    1-2 hours   ⏳ One-time setup
3. Download models          2 min       ⏳ One-time
4. streamlit run app.py     5 sec       ✓ Every time
5. Image upload             0 sec       ✓ Manual
6. Prediction               2-3 sec     ⏳ Automatic
7. View results             0 sec       ✓ Instant
───────────────────────────────────────────────
Total first time: 3+ hours
Total every time after: 5 seconds
```

---

## ✅ CHECKLIST BEFORE RUNNING

- [ ] Python 3.8+ installed? (python --version)
- [ ] In correct folder? (cd c:\Users\Asus\Desktop\medicalimmage)
- [ ] Requirements installed? (pip install -r requirements.txt)
- [ ] Models downloaded? (ls models/ shows two files)
- [ ] models/efficient_model.h5 exists? (40 MB)
- [ ] models/svm_model.pkl exists? (5 MB)
- [ ] Dataset present? (chest_xray/ folder with images)

**If all checked ✓**, run: `streamlit run app.py`

---

## 🎓 SAMPLE TEST IMAGES

To test the app, you can use images from:
```
chest_xray/test/NORMAL/
chest_xray/test/PNEUMONIA/
```

Or get test images:
```
- Kaggle: kaggle.com/search/chest xray
- Google Images: Search "chest X-ray normal" or "pneumonia"
- Medical databases: NIH, Radiopaedia
```

---

## 🚀 YOU'RE READY!

**Once models are trained:**
```bash
streamlit run app.py
# That's it! App runs!
```

---

**Still have questions?**
- Check QUICK_START.md
- Read docs/PROJECT_GUIDE.md
- See docs/VIVA_QUESTIONS.md for common issues

**Good luck! 🎉**
