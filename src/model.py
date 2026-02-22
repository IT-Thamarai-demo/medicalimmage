"""
ML MODEL MODULE
EfficientNetB0 + SVM classifier for pneumonia detection
"""

import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.models import Model
import numpy as np
from sklearn.svm import SVC
import joblib
import os


class PneumoniaDetector:
    """
    Pneumonia detection model using EfficientNetB0 + SVM
    """
    
    def __init__(self, img_size=224):
        self.img_size = img_size
        self.feature_extractor = None
        self.svm_classifier = None
        self.is_trained = False
    
    def get_feature_extractor(self):
        """
        Load pre-trained EfficientNetB0 for feature extraction.
        
        Returns:
        --------
        model : Keras Model
            EfficientNetB0 without top classification layer
        """
        print("Loading EfficientNetB0 (pre-trained on ImageNet)...")
        
        # Load pre-trained EfficientNetB0
        base_model = EfficientNetB0(
            weights='imagenet',
            include_top=False,
            pooling='avg',
            input_shape=(self.img_size, self.img_size, 1)
        )
        
        # Freeze base model layers
        base_model.trainable = False
        
        print(f"✓ EfficientNetB0 loaded with {len(base_model.layers)} layers")
        
        self.feature_extractor = base_model
        return base_model
    
    def extract_features(self, images):
        """
        Extract 1280 features from chest X-ray images.
        
        Parameters:
        -----------
        images : np.array
            Images array of shape (N, 224, 224, 1)
        
        Returns:
        --------
        features : np.array
            Extracted features of shape (N, 1280)
        """
        if self.feature_extractor is None:
            self.get_feature_extractor()
        
        print(f"Extracting features from {len(images)} images...")
        features = self.feature_extractor.predict(images, verbose=0)
        print(f"✓ Features extracted: shape {features.shape}")
        
        return features
    
    def train_svm(self, X_train_features, y_train):
        """
        Train SVM classifier on extracted features.
        
        Parameters:
        -----------
        X_train_features : np.array
            Extracted features (N, 1280)
        y_train : np.array
            Labels (N,) with 0=NORMAL, 1=PNEUMONIA
        """
        print(f"\nTraining SVM on {len(X_train_features)} samples...")
        
        # Create SVM with RBF kernel
        self.svm_classifier = SVC(
            kernel='rbf',
            C=1.0,
            gamma='scale',
            probability=True,
            verbose=1
        )
        
        # Train
        self.svm_classifier.fit(X_train_features, y_train)
        
        # Training accuracy
        train_accuracy = self.svm_classifier.score(X_train_features, y_train)
        print(f"✓ SVM trained! Training accuracy: {train_accuracy:.4f}")
        
        self.is_trained = True
    
    def predict(self, image_features):
        """
        Make prediction on image features.
        
        Parameters:
        -----------
        image_features : np.array
            Extracted features (1, 1280)
        
        Returns:
        --------
        prediction : int
            0 = NORMAL, 1 = PNEUMONIA
        confidence : float
            Confidence score (0-1)
        """
        if self.svm_classifier is None:
            raise ValueError("Model not trained. Call train_svm() first.")
        
        # Get prediction
        prediction = self.svm_classifier.predict(image_features)[0]
        
        # Get probability
        probabilities = self.svm_classifier.predict_proba(image_features)[0]
        confidence = probabilities[int(prediction)]
        
        return int(prediction), float(confidence)
    
    def save_model(self, feature_extractor_path='models/efficient_model.h5',
                   svm_path='models/svm_model.pkl'):
        """
        Save trained models.
        
        Parameters:
        -----------
        feature_extractor_path : str
            Path to save EfficientNet model
        svm_path : str
            Path to save SVM model
        """
        # Create models directory if needed
        os.makedirs(os.path.dirname(feature_extractor_path), exist_ok=True)
        os.makedirs(os.path.dirname(svm_path), exist_ok=True)
        
        # Save feature extractor
        if self.feature_extractor:
            self.feature_extractor.save(feature_extractor_path)
            print(f"✓ Feature extractor saved to {feature_extractor_path}")
        
        # Save SVM
        if self.svm_classifier:
            joblib.dump(self.svm_classifier, svm_path)
            print(f"✓ SVM model saved to {svm_path}")
    
    def load_model(self, feature_extractor_path='models/efficient_model.h5',
                   svm_path='models/svm_model.pkl'):
        """
        Load trained models.
        
        Parameters:
        -----------
        feature_extractor_path : str
            Path to saved EfficientNet model
        svm_path : str
            Path to saved SVM model
        """
        # Load feature extractor
        if os.path.exists(feature_extractor_path):
            self.feature_extractor = tf.keras.models.load_model(feature_extractor_path)
            print(f"✓ Feature extractor loaded from {feature_extractor_path}")
        
        # Load SVM
        if os.path.exists(svm_path):
            self.svm_classifier = joblib.load(svm_path)
            print(f"✓ SVM model loaded from {svm_path}")
            self.is_trained = True


# Convenience functions for backward compatibility
def get_feature_extractor(img_size=224):
    """Get pre-trained EfficientNetB0"""
    detector = PneumoniaDetector(img_size)
    return detector.get_feature_extractor()


def extract_features(model, img_array):
    """Extract features using EfficientNetB0"""
    features = model.predict(img_array, verbose=0)
    return features


def train_svm(X_train, y_train):
    """Train SVM classifier"""
    svm = SVC(kernel='rbf', probability=True, C=1.0, gamma='scale')
    svm.fit(X_train, y_train)
    return svm
