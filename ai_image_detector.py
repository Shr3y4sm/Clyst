"""
AI Image Detection Module
Detects AI-generated and AI-enhanced images using hybrid approach
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
        # Download image
        response = requests.get(image_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            return {'detected': False, 'score': 0, 'method': 'metadata_check', 'details': ['Failed to download image']}
        
        # Open with PIL
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
        # Download image
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
    
    # Step 3: Visual pattern analysis (only if numpy available)
    visual_result = {'detected': False, 'score': 0, 'details': []}
    if PIL_AVAILABLE and NUMPY_AVAILABLE:
        try:
            visual_result = analyze_visual_patterns(image_url)
        except Exception:
            pass
    
    # Combine scores with weighted approach
    # URL: 40%, Metadata: 35%, Visual: 25%
    combined_score = (
        url_result['score'] * 0.40 +
        metadata_result['score'] * 0.35 +
        visual_result['score'] * 0.25
    )
    
    # Collect all details
    all_details = {
        'url_analysis': url_result['details'],
        'metadata_analysis': metadata_result['details'],
        'visual_analysis': visual_result['details'],
        'url_score': url_result['score'],
        'metadata_score': metadata_result['score'],
        'visual_score': visual_result['score']
    }
    
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
    if visual_result['detected']:
        methods.append('visual patterns')
    
    primary_method = ', '.join(methods) if methods else 'heuristic analysis'
    
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
