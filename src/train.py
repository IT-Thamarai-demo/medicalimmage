# training_script.py
# Use this in Google Colab

import os
import numpy as np
import joblib
from src.data_loader import get_data_labels, load_and_preprocess_image
from src.model import get_feature_extractor, extract_features, train_svm
from tensorflow.keras.applications.efficientnet import preprocess_input

# 1. Setup paths
TRAIN_DIR = "chest_xray/train"
TEST_DIR = "chest_xray/test"

# 2. Get Filepaths and Labels
print("Loading data labels...")
train_files, train_labels = get_data_labels(TRAIN_DIR)
test_files, test_labels = get_data_labels(TEST_DIR)

# 3. Load Feature Extractor
print("Loading EfficientNetB0...")
model = get_feature_extractor()

# 4. Extract Features (This might take time)
def extract_all(files):
    features = []
    print(f"Extracting features from {len(files)} images...")
    for i, f in enumerate(files):
        img = load_and_preprocess_image(f)
        feat = extract_features(model, img)
        features.append(feat.flatten())
        if i % 100 == 0:
            print(f"Processed {i}/{len(files)}")
    return np.array(features)

X_train = extract_all(train_files)
X_test = extract_all(test_files)

# 5. Train SVM
print("Training SVM...")
svm_model = train_svm(X_train, train_labels)

# 6. Save Models
print("Saving models...")
# Note: we don't save the full EfficientNet since it's standard, 
# just the SVM weights. 
joblib.dump(svm_model, "pneumonia_svm_model.pkl")

print("Training Complete!")
