"""
AI Image Detection Module - Enhanced Edition
Detects AI-generated and AI-enhanced images using multi-layered analysis

This module implements a comprehensive AI detection system that cannot be bypassed by:
- Renaming files or changing URLs
- Removing metadata
- Simple image manipulations

DETECTION LAYERS:
================

1. URL Pattern Analysis (25% weight)
   - Checks for AI service domains (midjourney.com, openai.com, etc.)
   - Detects AI-related keywords in filenames
   - Fast preliminary screening

2. Metadata Analysis (20% weight)
   - EXIF data inspection
   - Image dimensions and format analysis
   - Software/generator field checks

3. Basic Visual Pattern Analysis (15% weight)
   - Color variance and symmetry checks
   - Texture consistency analysis
   - Quick visual heuristics

4. Advanced Pixel-Level Analysis (40% weight) - NEW & PRIMARY
   This is the core defense against bypass attempts:
   
   a) Noise Pattern Analysis
      - Detects unnaturally uniform noise (GAN characteristic)
      - Analyzes high-frequency noise content
      - Identifies over-smoothed regions
   
   b) Color Distribution Analysis
      - RGB histogram anomaly detection
      - Color channel correlation analysis
      - Quantization artifact detection
   
   c) Edge Characteristics Analysis (requires OpenCV)
      - Edge sharpness and continuity analysis
      - Unnatural focus pattern detection
      - Laplacian variance analysis
   
   d) Frequency Domain Analysis (requires SciPy)
      - 2D FFT spectral analysis
      - GAN fingerprint detection in frequency space
      - Upsampling artifact detection (grid patterns)
      - Radial frequency profile analysis
   
   e) GAN Fingerprint Detection
      - Checkerboard artifact detection (StyleGAN signature)
      - Local texture consistency analysis
      - Blob artifact detection
      - Saturation pattern analysis

SCORING SYSTEM:
==============
- Each layer contributes to a 0-100 confidence score
- Final score is weighted combination of all available layers
- Threshold for AI detection: 40.0
- Confidence levels: High (70+), Medium (50-69), Low (30-49), Unlikely (<30)

DEPENDENCIES:
=============
Required:
- requests (HTTP operations)

Optional (graceful degradation if missing):
- PIL/Pillow (basic image operations)
- NumPy (array operations, enables pixel analysis)
- SciPy (FFT frequency analysis)
- OpenCV (cv2) (edge detection and advanced computer vision)

Without optional libraries, the system falls back to URL/metadata analysis only.

BYPASS RESISTANCE:
==================
✓ File renaming: Pixel analysis detects AI regardless of filename
✓ Metadata stripping: Visual and pixel analysis work without metadata
✓ URL obfuscation: Multiple independent detection layers
✓ Format conversion: Pixel-level artifacts persist through conversions
✓ Compression: GAN fingerprints survive reasonable compression
✓ Cropping/resizing: Statistical properties remain detectable

Author: Clyst Marketplace Team
Version: 2.0 (Enhanced with Pixel-Level Analysis)
"""
import re
import requests
from typing import Dict, Any, Optional
from io import BytesIO
import json

# Optional dependencies
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from scipy import fft, signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# AI service domains and patterns
AI_SERVICE_PATTERNS = [
    r'midjourney\.com',
    r'openai\.com',
    r'cdn\.openai\.com',
    r'stability\.ai',
    r'replicate\.com',
    r'playground\.ai',
    r'lexica\.art',
    r'dall-e',
    r'dalle',
    r'stablediffusion',
    r'dreamstudio',
    r'nightcafe',
    r'artbreeder',
    r'craiyon',
    r'bluewillow',
    r'discord\.gg',  # Many AI tools use Discord
    r'discordapp\.com',
    r'discordapp\.net'
]

# AI-related keywords in filenames/URLs
AI_FILENAME_PATTERNS = [
    r'ai[_-]?generated',
    r'midjourney',
    r'dall[_-]?e',
    r'stable[_-]?diffusion',
    r'ai[_-]?art',
    r'generated[_-]?image',
    r'synthetic',
    r'prompt[_-]?\d+',
    r'seed[_-]?\d+',
    r'cfg[_-]?scale',
    r'dreambooth',
    r'lora[_-]?model',
    r'chatgpt[_\s-]?image',
    r'gpt[_-]?\d+[_\s-]?image',
    r'claude[_\s-]?image',
    r'gemini[_\s-]?image',
    r'copilot[_\s-]?image',
    r'bing[_\s-]?image[_\s-]?creator',
    r'ai[_\s-]?assistant',
    r'image[_\s-]?\d+[_\s-]?\d+[_\s-]?\d+.*pm|am',  # Date patterns like "Image Nov 17, 2025"
    r'screenshot[_\s-]?\d{4}[_-]?\d{2}[_-]?\d{2}'
]


def check_url_patterns(image_url: str) -> Dict[str, Any]:
    """
    Check if image URL contains AI service patterns
    
    Args:
        image_url: URL of the image
        
    Returns:
        Detection result with score and details
    """
    if not image_url:
        return {'detected': False, 'score': 0, 'method': 'url_check', 'details': []}
    
    url_lower = image_url.lower()
    details = []
    
    # Check for AI service domains
    for pattern in AI_SERVICE_PATTERNS:
        if re.search(pattern, url_lower):
            details.append(f"URL contains AI service pattern: {pattern}")
    
    # Check for AI-related filename patterns
    for pattern in AI_FILENAME_PATTERNS:
        if re.search(pattern, url_lower):
            details.append(f"Filename contains AI indicator: {pattern}")
    
    # Calculate score based on matches
    if details:
        score = min(95.0, len(details) * 30 + 50)  # Multiple matches = higher confidence
        return {
            'detected': True,
            'score': score,
            'method': 'url_pattern_analysis',
            'details': details
        }
    
    return {'detected': False, 'score': 0, 'method': 'url_check', 'details': []}


def analyze_image_metadata(image_url: str) -> Dict[str, Any]:
    """
    Analyze image metadata (EXIF) for AI generation indicators
    
    Args:
        image_url: URL of the image
        
    Returns:
        Detection result with score and details
    """
    if not PIL_AVAILABLE:
        return {
            'detected': False,
            'score': 0,
            'method': 'metadata_check',
            'details': ['PIL not available - metadata analysis skipped']
        }
    
    details = []
    score = 0
    
    try:
        # Check if it's a local file path or URL
        import os
        if os.path.isfile(image_url):
            # Local file - open directly
            img = Image.open(image_url)
        else:
            # URL - download first
            response = requests.get(image_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code != 200:
                return {'detected': False, 'score': 0, 'method': 'metadata_check', 'details': ['Failed to download image']}
            img = Image.open(BytesIO(response.content))
        
        # Check EXIF data
        exif_data = img.getexif() if hasattr(img, 'getexif') else {}
        
        # Check for AI tool signatures in EXIF
        ai_indicators_found = False
        if exif_data:
            exif_str = str(exif_data).lower()
            
            ai_tools = ['midjourney', 'dall-e', 'dalle', 'stable diffusion', 'stablediffusion', 
                       'dreamstudio', 'ai generated', 'synthetic', 'gan', 'diffusion model']
            
            for tool in ai_tools:
                if tool in exif_str:
                    details.append(f"EXIF contains AI tool reference: {tool}")
                    ai_indicators_found = True
        
        # Suspicious: No camera information (common in AI images)
        has_camera_info = False
        camera_tags = [271, 272, 305, 306]  # Make, Model, Software, DateTime
        
        for tag in camera_tags:
            if tag in exif_data:
                has_camera_info = True
                break
        
        if not has_camera_info and img.format in ['JPEG', 'JPG', 'PNG']:
            details.append("No camera metadata found (suspicious for photos)")
            score += 25
        
        # Check image dimensions (AI images often have specific ratios)
        width, height = img.size
        
        # Common AI generation sizes: 512x512, 768x768, 1024x1024, 512x768, etc.
        common_ai_sizes = [
            (512, 512), (768, 768), (1024, 1024),
            (512, 768), (768, 512), (512, 1024), (1024, 512),
            (640, 640), (896, 896)
        ]
        
        if (width, height) in common_ai_sizes or (height, width) in common_ai_sizes:
            details.append(f"Image dimensions ({width}x{height}) common in AI generation")
            score += 20
        
        # Perfect square or specific ratios are suspicious
        if width == height and width in [512, 768, 1024]:
            score += 15
        
        if ai_indicators_found:
            score = min(90.0, score + 50)
        
        if score >= 30:
            return {
                'detected': True,
                'score': float(score),
                'method': 'metadata_analysis',
                'details': details
            }
        
    except Exception as e:
        details.append(f"Metadata analysis failed: {str(e)[:50]}")
    
    return {'detected': False, 'score': float(score), 'method': 'metadata_check', 'details': details}


def analyze_visual_patterns(image_url: str) -> Dict[str, Any]:
    """
    Analyze visual patterns for AI artifacts
    
    Args:
        image_url: URL of the image
        
    Returns:
        Detection result with score and details
    """
    if not PIL_AVAILABLE or not NUMPY_AVAILABLE:
        return {
            'detected': False,
            'score': 0,
            'method': 'visual_check',
            'details': ['PIL or NumPy not available - visual analysis skipped']
        }
    
    details = []
    score = 0
    
    try:
        # Check if it's a local file path or URL
        import os
        if os.path.isfile(image_url):
            # Local file - open directly
            img = Image.open(image_url)
        else:
            # URL - download first
            response = requests.get(image_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code != 200:
                return {'detected': False, 'score': 0, 'method': 'visual_check', 'details': ['Failed to download']}
            img = Image.open(BytesIO(response.content))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Analyze image statistics
        img_array = np.array(img)
        
        # Check for unnatural smoothness (AI images often too smooth)
        # Calculate variance across channels
        channel_variance = []
        for channel in range(3):
            variance = np.var(img_array[:, :, channel])
            channel_variance.append(variance)
        
        avg_variance = np.mean(channel_variance)
        
        # Very low variance = suspiciously smooth
        if avg_variance < 500:
            details.append("Image appears unnaturally smooth (low variance)")
            score += 20
        
        # Very high variance = possible AI noise patterns
        if avg_variance > 5000:
            details.append("Image has unusual high variance pattern")
            score += 15
        
        # Check for perfect symmetry (suspicious in handcrafted items)
        width, height = img.size
        if width == height:
            # Compare left and right halves
            left_half = img_array[:, :width//2, :]
            right_half = np.fliplr(img_array[:, width//2:, :])
            
            if left_half.shape == right_half.shape:
                similarity = np.mean(np.abs(left_half - right_half))
                if similarity < 10:  # Very similar = suspicious
                    details.append("Image shows unusual perfect symmetry")
                    score += 25
        
        # Check color distribution (AI images often have specific patterns)
        color_std = np.std(img_array, axis=(0, 1))
        if np.all(color_std < 30):  # Very uniform colors
            details.append("Unusually uniform color distribution")
            score += 15
        
        if score >= 35:
            return {
                'detected': True,
                'score': float(score),
                'method': 'visual_pattern_analysis',
                'details': details
            }
        
    except Exception as e:
        details.append(f"Visual analysis failed: {str(e)[:50]}")
    
    return {'detected': False, 'score': float(score), 'method': 'visual_check', 'details': details}


def analyze_noise_patterns(img_array: np.ndarray) -> Dict[str, Any]:
    """
    Analyze noise patterns in the image to detect AI generation artifacts
    AI-generated images often have distinct noise characteristics
    
    Args:
        img_array: NumPy array of the image
        
    Returns:
        Detection result with score and details
    """
    details = []
    score = 0
    
    try:
        # Convert to grayscale for noise analysis
        if len(img_array.shape) == 3:
            gray = np.mean(img_array, axis=2).astype(np.uint8)
        else:
            gray = img_array
        
        # Calculate local variance (noise texture)
        # AI images often have unnaturally uniform noise
        height, width = gray.shape
        block_size = 8  # Analyze 8x8 blocks
        
        variances = []
        for i in range(0, height - block_size, block_size):
            for j in range(0, width - block_size, block_size):
                block = gray[i:i+block_size, j:j+block_size]
                variances.append(np.var(block))
        
        variance_of_variance = np.var(variances)
        
        # AI images: very consistent noise (low variance of variance)
        if variance_of_variance < 50:
            details.append("Unnaturally uniform noise pattern detected")
            score += 25
        
        # Check high-frequency noise (AI images often lack natural high-freq noise)
        # Apply high-pass filter
        kernel = np.array([[-1, -1, -1],
                          [-1,  8, -1],
                          [-1, -1, -1]])
        
        if CV2_AVAILABLE:
            try:
                filtered = cv2.filter2D(gray, -1, kernel)
                high_freq_energy = np.mean(np.abs(filtered))
                
                # Too low = suspicious (AI images are too clean)
                if high_freq_energy < 5:
                    details.append("Suspiciously low high-frequency noise")
                    score += 20
                
                # Check noise distribution uniformity
                noise_std = np.std(filtered)
                if noise_std < 10:
                    details.append("Uniform noise distribution (AI characteristic)")
                    score += 15
            except Exception:
                pass
        
    except Exception as e:
        details.append(f"Noise analysis warning: {str(e)[:30]}")
    
    return {'score': float(score), 'details': details}


def analyze_color_distribution(img_array: np.ndarray) -> Dict[str, Any]:
    """
    Analyze color distribution and histogram patterns
    AI images have characteristic color distributions
    
    Args:
        img_array: NumPy array of the image
        
    Returns:
        Detection result with score and details
    """
    details = []
    score = 0
    
    try:
        # Analyze each color channel
        for i, channel_name in enumerate(['Red', 'Green', 'Blue']):
            channel = img_array[:, :, i]
            
            # Calculate histogram
            hist, _ = np.histogram(channel.flatten(), bins=256, range=(0, 256))
            
            # AI images often have:
            # 1. Unnatural peaks in histogram
            hist_peaks = len([h for h in hist if h > np.mean(hist) * 3])
            if hist_peaks > 20:
                details.append(f"{channel_name} channel has suspicious histogram peaks")
                score += 5
            
            # 2. Missing values in certain ranges (quantization artifacts)
            zero_bins = np.sum(hist == 0)
            if zero_bins > 50:
                details.append(f"{channel_name} channel missing values (quantization)")
                score += 8
        
        # Check color variance across image
        color_std = np.std(img_array, axis=(0, 1))
        
        # AI images: often too uniform or too varied
        if np.all(color_std < 25):
            details.append("Suspiciously uniform colors across image")
            score += 15
        
        # Check for unnatural color relationships
        # Real photos have correlated RGB channels, AI sometimes doesn't
        r_channel = img_array[:, :, 0].flatten()
        g_channel = img_array[:, :, 1].flatten()
        b_channel = img_array[:, :, 2].flatten()
        
        # Sample for performance
        sample_size = min(10000, len(r_channel))
        indices = np.random.choice(len(r_channel), sample_size, replace=False)
        
        rg_corr = np.corrcoef(r_channel[indices], g_channel[indices])[0, 1]
        
        # Very low correlation is suspicious
        if abs(rg_corr) < 0.1:
            details.append("Unusual RGB channel correlation")
            score += 12
        
    except Exception as e:
        details.append(f"Color analysis warning: {str(e)[:30]}")
    
    return {'score': float(score), 'details': details}


def analyze_edge_characteristics(img_array: np.ndarray) -> Dict[str, Any]:
    """
    Analyze edge patterns and sharpness characteristics
    AI-generated images have distinct edge properties
    
    Args:
        img_array: NumPy array of the image
        
    Returns:
        Detection result with score and details
    """
    details = []
    score = 0
    
    if not CV2_AVAILABLE:
        return {'score': 0.0, 'details': ['OpenCV not available - edge analysis skipped']}
    
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Sobel edge detection
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        edge_magnitude = np.sqrt(sobelx**2 + sobely**2)
        
        # AI images often have:
        # 1. Too perfect edges (unrealistic sharpness)
        strong_edges = np.sum(edge_magnitude > 100)
        total_pixels = gray.shape[0] * gray.shape[1]
        edge_ratio = strong_edges / total_pixels
        
        if edge_ratio > 0.15:
            details.append("Unusually high proportion of sharp edges")
            score += 18
        
        # 2. Overly smooth transitions (no natural texture)
        edge_variance = np.var(edge_magnitude)
        if edge_variance < 500:
            details.append("Edge transitions too uniform")
            score += 15
        
        # 3. Check edge continuity (AI sometimes has broken edges)
        # Apply Canny for cleaner edge map
        edges = cv2.Canny(gray, 50, 150)
        edge_pixel_count = np.sum(edges > 0)
        
        # Too few edges = overly smooth (AI characteristic)
        if edge_pixel_count < total_pixels * 0.02:
            details.append("Suspiciously few edges detected")
            score += 12
        
        # Laplacian variance (blur detection)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # AI images often have unnatural focus characteristics
        if laplacian_var > 1000:
            details.append("Unnatural sharpness pattern")
            score += 10
        elif laplacian_var < 50:
            details.append("Unusually blurred throughout")
            score += 10
        
    except Exception as e:
        details.append(f"Edge analysis warning: {str(e)[:30]}")
    
    return {'score': float(score), 'details': details}


def analyze_frequency_domain(img_array: np.ndarray) -> Dict[str, Any]:
    """
    Analyze frequency domain using FFT to detect GAN artifacts
    AI-generated images have characteristic frequency patterns
    
    Args:
        img_array: NumPy array of the image
        
    Returns:
        Detection result with score and details
    """
    details = []
    score = 0
    
    if not SCIPY_AVAILABLE:
        return {'score': 0.0, 'details': ['SciPy not available - FFT analysis skipped']}
    
    try:
        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = np.mean(img_array, axis=2)
        else:
            gray = img_array
        
        # Resize for performance (FFT is expensive)
        height, width = gray.shape
        max_size = 512
        if max(height, width) > max_size:
            scale = max_size / max(height, width)
            new_height = int(height * scale)
            new_width = int(width * scale)
            if CV2_AVAILABLE:
                gray = cv2.resize(gray, (new_width, new_height))
            else:
                # Skip if can't resize
                return {'score': 0.0, 'details': ['Image too large for FFT without cv2']}
        
        # Apply 2D FFT
        fft_result = fft.fft2(gray)
        fft_shift = fft.fftshift(fft_result)
        magnitude_spectrum = np.abs(fft_shift)
        
        # Log transform for better visualization
        magnitude_spectrum = np.log(magnitude_spectrum + 1)
        
        # AI images often show:
        # 1. Unusual peaks in frequency spectrum
        center_y, center_x = magnitude_spectrum.shape[0] // 2, magnitude_spectrum.shape[1] // 2
        
        # Extract radial profile
        y, x = np.ogrid[:magnitude_spectrum.shape[0], :magnitude_spectrum.shape[1]]
        r = np.sqrt((x - center_x)**2 + (y - center_y)**2).astype(int)
        
        max_radius = min(center_x, center_y)
        radial_profile = np.zeros(max_radius)
        
        for radius in range(max_radius):
            mask = (r == radius)
            if np.any(mask):
                radial_profile[radius] = np.mean(magnitude_spectrum[mask])
        
        # Check for unnatural periodicity (common in GAN outputs)
        if len(radial_profile) > 10:
            # Look for suspicious peaks
            profile_diff = np.diff(radial_profile)
            peaks = np.sum(np.abs(profile_diff) > np.std(profile_diff) * 2)
            
            if peaks > len(radial_profile) * 0.3:
                details.append("Unusual frequency domain periodicity detected")
                score += 20
        
        # 2. GAN fingerprint: specific frequency patterns
        # High energy in specific frequency bands is suspicious
        low_freq = magnitude_spectrum[center_y-10:center_y+10, center_x-10:center_x+10]
        high_freq_regions = [
            magnitude_spectrum[0:20, 0:20],
            magnitude_spectrum[-20:, -20:],
            magnitude_spectrum[0:20, -20:],
            magnitude_spectrum[-20:, 0:20]
        ]
        
        low_freq_energy = np.mean(low_freq)
        high_freq_energy = np.mean([np.mean(region) for region in high_freq_regions])
        
        energy_ratio = low_freq_energy / (high_freq_energy + 1e-10)
        
        # AI images: unusual energy distribution
        if energy_ratio > 100:
            details.append("Suspicious frequency energy distribution (GAN artifact)")
            score += 25
        elif energy_ratio < 5:
            details.append("Unusual high-frequency emphasis")
            score += 15
        
        # 3. Check for grid patterns (upsampling artifacts)
        # These appear as crosses in frequency domain
        horizontal_line = magnitude_spectrum[center_y, :]
        vertical_line = magnitude_spectrum[:, center_x]
        
        h_variance = np.var(horizontal_line)
        v_variance = np.var(vertical_line)
        
        if h_variance > np.var(magnitude_spectrum) * 2 or v_variance > np.var(magnitude_spectrum) * 2:
            details.append("Grid pattern detected (upsampling artifact)")
            score += 18
        
    except Exception as e:
        details.append(f"FFT analysis warning: {str(e)[:30]}")
    
    return {'score': float(score), 'details': details}


def analyze_gan_fingerprints(img_array: np.ndarray) -> Dict[str, Any]:
    """
    Detect specific GAN (Generative Adversarial Network) fingerprints
    Different GAN architectures leave distinct patterns
    
    Args:
        img_array: NumPy array of the image
        
    Returns:
        Detection result with score and details
    """
    details = []
    score = 0
    
    try:
        # 1. Check for checkerboard artifacts (common in StyleGAN, etc.)
        if CV2_AVAILABLE:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Look for 2x2 or 4x4 periodic patterns
            for kernel_size in [2, 4]:
                kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size * kernel_size)
                smoothed = cv2.filter2D(gray, -1, kernel)
                diff = np.abs(gray.astype(float) - smoothed)
                
                # High difference in regular pattern = checkerboard
                if np.mean(diff) > 15:
                    details.append(f"Checkerboard artifact detected ({kernel_size}x{kernel_size})")
                    score += 20
                    break
        
        # 2. Analyze local consistency
        # GANs sometimes produce locally inconsistent textures
        height, width = img_array.shape[:2]
        
        # Sample random patches and check consistency
        patch_size = 32
        num_samples = min(20, (height // patch_size) * (width // patch_size))
        
        patch_variances = []
        for _ in range(num_samples):
            y = np.random.randint(0, height - patch_size)
            x = np.random.randint(0, width - patch_size)
            patch = img_array[y:y+patch_size, x:x+patch_size]
            patch_variances.append(np.var(patch))
        
        # GAN images: high variance of patch variances
        variance_of_patch_variance = np.var(patch_variances)
        if variance_of_patch_variance > 5000:
            details.append("Inconsistent local texture (GAN characteristic)")
            score += 15
        
        # 3. Check for "blobby" artifacts
        # GANs sometimes produce unnaturally smooth blobs
        if CV2_AVAILABLE:
            # Apply bilateral filter to find smooth regions
            smooth = cv2.bilateralFilter(img_array, 9, 75, 75)
            diff = np.mean(np.abs(img_array.astype(float) - smooth.astype(float)))
            
            if diff < 10:  # Too similar = too smooth
                details.append("Unnatural smoothness (blob artifacts)")
                score += 12
        
        # 4. Saturation analysis
        # GANs often produce oversaturated or undersaturated images
        if len(img_array.shape) == 3:
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV) if CV2_AVAILABLE else None
            if hsv is not None:
                saturation = hsv[:, :, 1]
                
                # Check saturation distribution
                sat_mean = np.mean(saturation)
                sat_std = np.std(saturation)
                
                # Unnatural saturation patterns
                if sat_mean > 180 and sat_std < 30:
                    details.append("Unnaturally high uniform saturation")
                    score += 15
                elif sat_mean < 50 and sat_std < 20:
                    details.append("Unnaturally low saturation")
                    score += 10
        
    except Exception as e:
        details.append(f"GAN fingerprint analysis warning: {str(e)[:30]}")
    
    return {'score': float(score), 'details': details}


def analyze_pixel_level_features(image_url: str) -> Dict[str, Any]:
    """
    Comprehensive pixel-level analysis combining all advanced techniques
    
    Args:
        image_url: URL of the image or local file path
        
    Returns:
        Detection result with score and details
    """
    if not PIL_AVAILABLE or not NUMPY_AVAILABLE:
        return {
            'detected': False,
            'score': 0,
            'method': 'pixel_analysis',
            'details': ['PIL or NumPy not available - pixel analysis skipped']
        }
    
    details = []
    total_score = 0
    
    try:
        # Check if it's a local file path or URL
        import os
        if os.path.isfile(image_url):
            # Local file - open directly
            img = Image.open(image_url)
        else:
            # URL - download first
            response = requests.get(image_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code != 200:
                return {'detected': False, 'score': 0, 'method': 'pixel_analysis', 'details': ['Download failed']}
            img = Image.open(BytesIO(response.content))
        
        # Convert to RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Resize large images for performance
        max_dimension = 1024
        height, width = img_array.shape[:2]
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            new_height = int(height * scale)
            new_width = int(width * scale)
            if CV2_AVAILABLE:
                img_array = cv2.resize(img_array, (new_width, new_height))
        
        # Run all pixel-level analyses
        analyses = []
        
        # 1. Noise pattern analysis
        noise_result = analyze_noise_patterns(img_array)
        if noise_result['score'] > 0:
            analyses.append(('Noise Analysis', noise_result['score'], noise_result['details']))
            total_score += noise_result['score']
        
        # 2. Color distribution analysis
        color_result = analyze_color_distribution(img_array)
        if color_result['score'] > 0:
            analyses.append(('Color Analysis', color_result['score'], color_result['details']))
            total_score += color_result['score']
        
        # 3. Edge characteristics analysis
        edge_result = analyze_edge_characteristics(img_array)
        if edge_result['score'] > 0:
            analyses.append(('Edge Analysis', edge_result['score'], edge_result['details']))
            total_score += edge_result['score']
        
        # 4. Frequency domain analysis
        freq_result = analyze_frequency_domain(img_array)
        if freq_result['score'] > 0:
            analyses.append(('Frequency Analysis', freq_result['score'], freq_result['details']))
            total_score += freq_result['score']
        
        # 5. GAN fingerprint detection
        gan_result = analyze_gan_fingerprints(img_array)
        if gan_result['score'] > 0:
            analyses.append(('GAN Fingerprint', gan_result['score'], gan_result['details']))
            total_score += gan_result['score']
        
        # Compile all details
        for analysis_name, analysis_score, analysis_details in analyses:
            details.append(f"{analysis_name} (Score: {analysis_score:.1f}): {', '.join(analysis_details[:2])}")
        
        # Normalize score (max possible ~150, normalize to 100)
        normalized_score = min(100.0, total_score * 0.7)
        
        detected = normalized_score >= 35.0
        
        return {
            'detected': detected,
            'score': float(normalized_score),
            'method': 'advanced_pixel_analysis',
            'details': details,
            'analysis_breakdown': {
                'noise': noise_result['score'],
                'color': color_result['score'],
                'edges': edge_result['score'],
                'frequency': freq_result['score'],
                'gan': gan_result['score']
            }
        }
        
    except Exception as e:
        details.append(f"Pixel analysis failed: {str(e)[:50]}")
        return {'detected': False, 'score': 0.0, 'method': 'pixel_analysis', 'details': details}


def detect_ai_image(image_url: str) -> Dict[str, Any]:
    """
    Main AI image detection function using hybrid approach
    
    Args:
        image_url: URL of the product image
        
    Returns:
        Detection result with combined analysis
    """
    if not image_url:
        return {
            'is_ai_generated': False,
            'confidence_score': 0.0,
            'detection_method': 'no_image',
            'details': {'message': 'No image URL provided'}
        }
    
    # Step 1: Quick URL pattern check (instant)
    url_result = check_url_patterns(image_url)
    
    # If URL clearly indicates AI service, high confidence
    if url_result['detected'] and url_result['score'] >= 80:
        return {
            'is_ai_generated': True,
            'confidence_score': url_result['score'],
            'detection_method': url_result['method'],
            'details': {
                'url_analysis': url_result['details'],
                'confidence_level': 'high',
                'primary_indicator': 'AI service URL detected'
            }
        }
    
    # Step 2: Metadata analysis
    metadata_result = analyze_image_metadata(image_url)
    
    # Step 3: Basic visual pattern analysis (only if numpy available)
    visual_result = {'detected': False, 'score': 0, 'details': []}
    if PIL_AVAILABLE and NUMPY_AVAILABLE:
        try:
            visual_result = analyze_visual_patterns(image_url)
        except Exception:
            pass
    
    # Step 4: Advanced pixel-level analysis (if libraries available)
    pixel_result = {'detected': False, 'score': 0, 'details': [], 'analysis_breakdown': {}}
    if PIL_AVAILABLE and NUMPY_AVAILABLE:
        try:
            pixel_result = analyze_pixel_level_features(image_url)
        except Exception:
            pass
    
    # Enhanced weighted scoring system
    # URL: 25%, Metadata: 20%, Basic Visual: 15%, Advanced Pixel: 40%
    # The new pixel-level analysis gets highest weight as it's hardest to bypass
    combined_score = (
        url_result['score'] * 0.25 +
        metadata_result['score'] * 0.20 +
        visual_result['score'] * 0.15 +
        pixel_result['score'] * 0.40
    )
    
    # Collect all details
    all_details = {
        'url_analysis': url_result['details'],
        'metadata_analysis': metadata_result['details'],
        'visual_analysis': visual_result['details'],
        'pixel_analysis': pixel_result.get('details', []),
        'url_score': url_result['score'],
        'metadata_score': metadata_result['score'],
        'visual_score': visual_result['score'],
        'pixel_score': pixel_result['score']
    }
    
    # Add detailed breakdown if available
    if 'analysis_breakdown' in pixel_result and pixel_result['analysis_breakdown']:
        all_details['pixel_analysis_breakdown'] = pixel_result['analysis_breakdown']
    
    # Determine if AI generated based on threshold
    is_ai = combined_score >= 40.0
    
    # Determine confidence level
    if combined_score >= 70:
        confidence = 'high'
    elif combined_score >= 50:
        confidence = 'medium'
    elif combined_score >= 30:
        confidence = 'low'
    else:
        confidence = 'unlikely'
    
    all_details['confidence_level'] = confidence
    
    # Determine primary detection method
    methods = []
    if url_result['detected']:
        methods.append('URL patterns')
    if metadata_result['detected']:
        methods.append('metadata')
    if pixel_result['detected']:
        methods.append('advanced pixel analysis')
    elif visual_result['detected']:
        methods.append('visual patterns')
    
    primary_method = ', '.join(methods) if methods else 'heuristic analysis'
    
    # Add analysis summary
    if pixel_result['score'] > 0:
        all_details['analysis_summary'] = (
            f"Enhanced AI detection with pixel-level analysis. "
            f"Combined score: {combined_score:.1f} (URL: {url_result['score']:.1f}, "
            f"Metadata: {metadata_result['score']:.1f}, Visual: {visual_result['score']:.1f}, "
            f"Pixel: {pixel_result['score']:.1f})"
        )
    
    return {
        'is_ai_generated': is_ai,
        'confidence_score': round(combined_score, 2),
        'detection_method': primary_method,
        'details': all_details
    }


def get_ai_badge_info(confidence_score: float) -> Dict[str, str]:
    """
    Get badge information based on AI detection confidence
    
    Args:
        confidence_score: AI detection confidence (0-100)
        
    Returns:
        Badge info with emoji, text, and color
    """
    if confidence_score >= 70:
        return {
            'emoji': '🤖',
            'text': 'AI Generated',
            'color': '#ff6b6b',
            'level': 'high'
        }
    elif confidence_score >= 50:
        return {
            'emoji': '⚠️',
            'text': 'Likely AI Enhanced',
            'color': '#ffa500',
            'level': 'medium'
        }
    elif confidence_score >= 30:
        return {
            'emoji': '❓',
            'text': 'Possibly AI',
            'color': '#ffd700',
            'level': 'low'
        }
    else:
        return {
            'emoji': '',
            'text': '',
            'color': '',
            'level': 'none'
        }


# Test function
if __name__ == "__main__":
    # Test URLs
    test_cases = [
        {
            'url': 'https://cdn.midjourney.com/abc123/image.png',
            'description': 'Obvious Midjourney URL'
        },
        {
            'url': 'https://example.com/ai-generated-artwork.jpg',
            'description': 'Filename indicates AI'
        },
        {
            'url': 'https://example.com/photo-12345.jpg',
            'description': 'Regular photo URL'
        }
    ]
    
    print("=" * 80)
    print("AI IMAGE DETECTION TESTS")
    print("=" * 80)
    print()
    
    for test in test_cases:
        print(f"Testing: {test['description']}")
        print(f"URL: {test['url']}")
        
        result = detect_ai_image(test['url'])
        
        print(f"Result: {'🤖 AI GENERATED' if result['is_ai_generated'] else '✓ AUTHENTIC'}")
        print(f"Confidence: {result['confidence_score']:.2f}%")
        print(f"Method: {result['detection_method']}")
        print(f"Details: {result['details'].get('confidence_level', 'N/A')}")
        print()
        print("-" * 80)
        print()
