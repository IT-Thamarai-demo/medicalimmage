"""
DATA LOADER MODULE
Loads chest X-ray images from local chest_xray/ folder
"""

import os
import numpy as np
import cv2
from PIL import Image
from pathlib import Path


def load_images_from_folder(folder_path, img_size=224):
    """
    Load all images from a folder and preprocess them.
    
    Parameters:
    -----------
    folder_path : str
        Path to folder containing images
    img_size : int
        Target image size (224x224 for EfficientNetB0)
    
    Returns:
    --------
    images : np.array
        Array of preprocessed images (N, img_size, img_size, 1)
    """
    images = []
    image_files = [f for f in os.listdir(folder_path) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    for img_file in image_files:
        img_path = os.path.join(folder_path, img_file)
        try:
            # Read image in grayscale
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            
            if img is None:
                print(f"Warning: Could not read {img_path}")
                continue
            
            # Resize to target size
            img = cv2.resize(img, (img_size, img_size))
            
            # Normalize to 0-1
            img = img.astype(np.float32) / 255.0
            
            # Add channel dimension: (224, 224) → (224, 224, 1)
            img = np.expand_dims(img, axis=-1)
            
            images.append(img)
            
        except Exception as e:
            print(f"Error processing {img_file}: {e}")
            continue
    
    return np.array(images)


def load_dataset(dataset_path='chest_xray', img_size=224):
    """
    Load entire chest X-ray dataset (train, test, val).
    
    Parameters:
    -----------
    dataset_path : str
        Path to chest_xray folder
    img_size : int
        Target image size
    
    Returns:
    --------
    X_train, y_train : Training images and labels
    X_test, y_test : Testing images and labels
    X_val, y_val : Validation images and labels
    """
    
    print(f"Loading dataset from {dataset_path}...")
    
    data = {}
    
    # Load train, test, val sets
    for split in ['train', 'test', 'val']:
        split_path = os.path.join(dataset_path, split)
        
        # Load NORMAL images (label = 0)
        normal_path = os.path.join(split_path, 'NORMAL')
        normal_images = load_images_from_folder(normal_path, img_size)
        normal_labels = np.zeros(len(normal_images))
        
        # Load PNEUMONIA images (label = 1)
        pneumonia_path = os.path.join(split_path, 'PNEUMONIA')
        pneumonia_images = load_images_from_folder(pneumonia_path, img_size)
        pneumonia_labels = np.ones(len(pneumonia_images))
        
        # Combine and shuffle
        X = np.vstack([normal_images, pneumonia_images])
        y = np.hstack([normal_labels, pneumonia_labels])
        
        # Shuffle
        shuffle_idx = np.random.permutation(len(X))
        X = X[shuffle_idx]
        y = y[shuffle_idx]
        
        data[split] = (X, y)
        
        print(f"✓ {split.upper()}: {len(X)} images (Normal: {int(sum(y==0))}, Pneumonia: {int(sum(y==1))})")
    
    X_train, y_train = data['train']
    X_test, y_test = data['test']
    X_val, y_val = data['val']
    
    print("\n✅ Dataset loaded successfully!")
    
    return X_train, y_train, X_test, y_test, X_val, y_val


def preprocess_image(image_path, img_size=224):
    """
    Preprocess a single image for inference.
    
    Parameters:
    -----------
    image_path : str
        Path to image file
    img_size : int
        Target image size
    
    Returns:
    --------
    img : np.array
        Preprocessed image (1, img_size, img_size, 1)
    """
    # Read image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    # Resize
    img = cv2.resize(img, (img_size, img_size))
    
    # Normalize
    img = img.astype(np.float32) / 255.0
    
    # Add dimensions: (H, W) → (1, H, W, 1)
    img = np.expand_dims(img, axis=0)
    img = np.expand_dims(img, axis=-1)
    
    return img


def preprocess_pil_image(pil_image, img_size=224):
    """
    Preprocess a PIL Image object (useful for Streamlit).
    
    Parameters:
    -----------
    pil_image : PIL.Image
        PIL Image object
    img_size : int
        Target image size
    
    Returns:
    --------
    img : np.array
        Preprocessed image (1, img_size, img_size, 1)
    """
    # Convert to numpy array
    img_array = np.array(pil_image)
    
    # Convert to grayscale if needed
    if len(img_array.shape) == 3:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Resize
    img_array = cv2.resize(img_array, (img_size, img_size))
    
    # Normalize
    img_array = img_array.astype(np.float32) / 255.0
    
    # Add dimensions
    img_array = np.expand_dims(img_array, axis=0)
    img_array = np.expand_dims(img_array, axis=-1)
    
    return img_array

def get_data_labels(directory):
    """
    Scans directory and returns list of file paths and labels (0 for Normal, 1 for Pneumonia).
    """
    filepaths = []
    labels = []
    
    for label_name in ['NORMAL', 'PNEUMONIA']:
        label_val = 0 if label_name == 'NORMAL' else 1
        class_dir = os.path.join(directory, label_name)
        
        if not os.path.exists(class_dir):
            continue
            
        for img_name in os.listdir(class_dir):
            if img_name.endswith(('.jpeg', '.jpg', '.png')):
                filepaths.append(os.path.join(class_dir, img_name))
                labels.append(label_val)
                
    return filepaths, np.array(labels)
