"""
GRAD-CAM MODULE
Generate heatmaps showing which parts of X-ray influenced the prediction
"""

import numpy as np
import tensorflow as tf
import cv2
import matplotlib.cm as cm


def make_gradcam_heatmap(img_array, model, last_conv_layer_name, pred_index=None):
    """
    Generates a Grad-CAM heatmap for a given image.
    
    Parameters:
    -----------
    img_array : np.array
        Input image array (1, 224, 224, 1)
    model : Keras Model
        The feature extraction model
    last_conv_layer_name : str
        Name of the last convolutional layer
    pred_index : int
        Class index (0=NORMAL, 1=PNEUMONIA)
    
    Returns:
    --------
    heatmap : np.array
        Grad-CAM heatmap (224, 224)
    """
    # Create model that outputs both conv features and predictions
    grad_model = tf.keras.models.Model(
        [model.inputs],
        [model.get_layer(last_conv_layer_name).output, model.output]
    )

    # Compute gradients
    with tf.GradientTape() as tape:
        last_conv_layer_output, preds = grad_model(img_array)
        
        if pred_index is None:
            pred_index = tf.argmax(preds[0])
        
        class_channel = preds[:, pred_index]

    # Get gradients
    grads = tape.gradient(class_channel, last_conv_layer_output)
    
    # Average gradients spatially
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # Weight conv outputs by gradients
    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    # ReLU and normalize
    heatmap = tf.maximum(heatmap, 0) / (tf.reduce_max(heatmap) + 1e-10)
    
    return heatmap.numpy()


def overlay_heatmap_on_image(image, heatmap, alpha=0.4, colormap='jet'):
    """
    Overlay Grad-CAM heatmap on original image.
    
    Parameters:
    -----------
    image : np.array
        Original image (224, 224, 1) normalized to 0-1
    heatmap : np.array
        Grad-CAM heatmap (224, 224) normalized to 0-1
    alpha : float
        Transparency of heatmap overlay
    colormap : str
        Matplotlib colormap name
    
    Returns:
    --------
    overlay : np.array
        Overlaid image (224, 224, 3) in 0-255 range
    """
    # Convert image to 0-255 range if grayscale
    if len(image.shape) == 2 or image.shape[2] == 1:
        img_display = (image.squeeze() * 255).astype(np.uint8)
        img_display = cv2.cvtColor(img_display, cv2.COLOR_GRAY2RGB)
    else:
        img_display = (image * 255).astype(np.uint8)

    # Convert heatmap to 0-255
    heatmap_uint8 = (heatmap * 255).astype(np.uint8)
    
    # Resize heatmap to match image
    heatmap_uint8 = cv2.resize(heatmap_uint8, (224, 224))
    
    # Apply colormap
    cmap = cm.get_cmap(colormap)
    heatmap_colored = cmap(heatmap_uint8 / 255.0)
    heatmap_rgb = (heatmap_colored[:, :, :3] * 255).astype(np.uint8)
    
    # Convert to BGR for OpenCV
    heatmap_bgr = cv2.cvtColor(heatmap_rgb, cv2.COLOR_RGB2BGR)
    
    # Blend images
    overlay = cv2.addWeighted(img_display, 1-alpha, heatmap_bgr, alpha, 0)
    
    return overlay


def create_heatmap_visualization(image, heatmap, colormap='jet'):
    """
    Create a standalone heatmap visualization.
    
    Parameters:
    -----------
    image : np.array
        Original image (224, 224, 1)
    heatmap : np.array
        Grad-CAM heatmap (224, 224)
    colormap : str
        Colormap name
    
    Returns:
    --------
    heatmap_viz : np.array
        Heatmap visualization (224, 224, 3) in 0-255 range
    """
    # Resize heatmap
    heatmap_resized = cv2.resize(heatmap, (224, 224))
    
    # Normalize to 0-1
    heatmap_normalized = (heatmap_resized - heatmap_resized.min()) / \
                         (heatmap_resized.max() - heatmap_resized.min() + 1e-10)
    
    # Apply colormap
    cmap = cm.get_cmap(colormap)
    heatmap_colored = cmap(heatmap_normalized)
    heatmap_rgb = (heatmap_colored[:, :, :3] * 255).astype(np.uint8)
    
    # Convert to BGR
    heatmap_bgr = cv2.cvtColor(heatmap_rgb, cv2.COLOR_RGB2BGR)
    
    return heatmap_bgr


def get_conv_layer_name(model):
    """
    Find the last convolutional layer in the model.
    
    Parameters:
    -----------
    model : Keras Model
        The neural network model
    
    Returns:
    --------
    layer_name : str
        Name of last convolutional layer
    """
    conv_layer_name = None
    
    for layer in model.layers:
        if 'conv' in layer.name:
            conv_layer_name = layer.name
    
    if conv_layer_name is None:
        # Default for EfficientNetB0
        conv_layer_name = model.layers[-1].name
    
    return conv_layer_name

def save_and_display_gradcam(img_path, heatmap, alpha=0.4):
    """
    Superimposes the heatmap on the original image.
    """
    img = cv2.imread(img_path)
    img = cv2.resize(img, (224, 224))

    heatmap = np.uint8(255 * heatmap)
    jet = cm.get_cmap("jet")
    jet_colors = jet(np.arange(256))[:, :3]
    jet_heatmap = jet_colors[heatmap]

    jet_heatmap = tf.keras.preprocessing.image.array_to_img(jet_heatmap)
    jet_heatmap = jet_heatmap.resize((img.shape[1], img.shape[0]))
    jet_heatmap = tf.keras.preprocessing.image.img_to_array(jet_heatmap)

    superimposed_img = jet_heatmap * alpha + img
    superimposed_img = tf.keras.preprocessing.image.array_to_img(superimposed_img)

    return superimposed_img
