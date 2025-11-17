"""
Sustainability Classification Module
Classifies products as sustainable based on image and text analysis
"""
import json
import re
from typing import Dict, Any, List

# Sustainability keywords with weights
SUSTAINABLE_KEYWORDS = {
    'high_score': {
        'keywords': [
            'handmade', 'hand-made', 'hand made', 'organic', 'recycled', 'upcycled',
            'natural', 'eco-friendly', 'eco friendly', 'biodegradable', 'sustainable',
            'bamboo', 'jute', 'cotton', 'clay', 'ceramic', 'pottery', 'wood', 'wooden',
            'artisan', 'heritage', 'traditional', 'handcrafted', 'hand-crafted',
            'eco', 'green', 'earth-friendly', 'environmentally friendly'
        ],
        'weight': 10
    },
    'medium_score': {
        'keywords': [
            'reusable', 'plant-based', 'non-toxic', 'renewable', 'ethical',
            'fair-trade', 'fair trade', 'local', 'locally made', 'artisanal',
            'craft', 'crafted', 'homemade', 'home-made', 'natural fiber',
            'natural fibre', 'biodegradable', 'compostable', 'vintage',
            'repurposed', 'reclaimed', 'salvaged'
        ],
        'weight': 7
    },
    'low_score': {
        'keywords': [
            'handwoven', 'hand-woven', 'hand woven', 'textile', 'fabric',
            'metal', 'brass', 'copper', 'bronze', 'terracotta', 'terra-cotta',
            'stone', 'marble', 'leather', 'silk', 'wool', 'linen'
        ],
        'weight': 4
    },
    'negative': {
        'keywords': [
            'plastic', 'synthetic', 'chemical', 'mass-produced', 'factory-made',
            'polyester', 'acrylic', 'nylon', 'artificial'
        ],
        'weight': -8
    }
}


def analyze_text_sustainability(text: str) -> Dict[str, Any]:
    """
    Analyze product title and description for sustainability indicators
    
    Args:
        text: Combined title and description
        
    Returns:
        Dictionary with score and matching keywords
    """
    if not text:
        return {'score': 0.0, 'keywords_found': [], 'reasons': []}
    
    text_lower = text.lower()
    total_score = 0
    keywords_found = []
    reasons = []
    
    # Check each keyword category
    for category, data in SUSTAINABLE_KEYWORDS.items():
        for keyword in data['keywords']:
            if keyword in text_lower:
                total_score += data['weight']
                keywords_found.append(keyword)
                
                # Add reason for high-weight keywords
                if data['weight'] >= 7:
                    if category == 'high_score':
                        reasons.append(f"Contains '{keyword}' - strong sustainability indicator")
                    elif category == 'medium_score':
                        reasons.append(f"Uses '{keyword}' material/method")
                elif data['weight'] < 0:
                    reasons.append(f"Contains '{keyword}' - may not be sustainable")
    
    # Normalize score to 0-100 scale
    # Max possible score: ~15 high keywords * 10 = 150
    # Normalize to percentage
    normalized_score = min(100, max(0, (total_score / 150) * 100 + 30))  # Base score of 30
    
    return {
        'score': round(normalized_score, 2),
        'keywords_found': list(set(keywords_found)),
        'reasons': reasons[:5]  # Limit to top 5 reasons
    }


def analyze_image_sustainability(image_url: str) -> Dict[str, Any]:
    """
    Analyze product image for sustainability indicators
    This is a simplified heuristic-based approach
    
    Args:
        image_url: URL of the product image
        
    Returns:
        Dictionary with score and confidence
    """
    # For now, we'll use a heuristic approach
    # In a production system, this would use a trained CNN model
    
    # Base score for handcrafted products (artisan marketplace assumption)
    base_score = 55.0
    
    # Image-based heuristics could include:
    # - Natural texture detection (would require actual image processing)
    # - Color palette analysis (earth tones vs synthetic colors)
    # - Pattern recognition (traditional vs modern/industrial)
    
    # Since we don't have actual image processing here,
    # we'll return a moderate base score for artisan products
    return {
        'score': base_score,
        'confidence': 0.6,
        'method': 'heuristic_artisan_base'
    }


def classify_product_sustainability(
    title: str,
    description: str,
    image_url: str = None
) -> Dict[str, Any]:
    """
    Main classification function combining text and image analysis
    
    Args:
        title: Product title
        description: Product description
        image_url: Product image URL (optional)
        
    Returns:
        Classification result with score, decision, and reasons
    """
    # Combine title and description
    combined_text = f"{title} {description}" if title and description else (title or description or "")
    
    # Text analysis (weighted 70% for reliability)
    text_result = analyze_text_sustainability(combined_text)
    text_score = text_result['score']
    
    # Image analysis (weighted 30%)
    image_score = 55.0  # Default artisan marketplace base score
    if image_url:
        image_result = analyze_image_sustainability(image_url)
        image_score = image_result['score']
    
    # Calculate weighted final score
    final_score = (text_score * 0.7) + (image_score * 0.3)
    
    # Classification threshold
    is_sustainable = final_score >= 60.0
    
    # Generate comprehensive reasons
    reasons = text_result['reasons'].copy()
    
    # Add general reasons based on score
    if is_sustainable:
        if text_result['keywords_found']:
            top_keywords = text_result['keywords_found'][:3]
            reasons.insert(0, f"✓ Sustainable materials/methods detected: {', '.join(top_keywords)}")
        reasons.insert(0, "✓ Classified as sustainable handcrafted product")
    else:
        reasons.insert(0, "Product may not meet sustainability criteria")
    
    # Add artisan marketplace context
    if final_score >= 50:
        reasons.append("Handcrafted artisan product from Clyst marketplace")
    
    return {
        'is_sustainable': is_sustainable,
        'score': round(final_score, 2),
        'text_score': round(text_score, 2),
        'image_score': round(image_score, 2),
        'reasons': reasons[:6],  # Top 6 reasons
        'keywords_found': text_result['keywords_found'][:10]  # Top 10 keywords
    }


def get_sustainability_badge_info(score: float) -> Dict[str, str]:
    """
    Get badge information based on sustainability score
    
    Args:
        score: Sustainability score (0-100)
        
    Returns:
        Badge info with emoji, text, and color
    """
    if score >= 80:
        return {
            'emoji': '🌿',
            'text': 'Highly Sustainable',
            'color': '#28a745'
        }
    elif score >= 60:
        return {
            'emoji': '🌱',
            'text': 'Sustainable Product',
            'color': '#5cb85c'
        }
    elif score >= 40:
        return {
            'emoji': '♻️',
            'text': 'Eco-Conscious',
            'color': '#5bc0de'
        }
    else:
        return {
            'emoji': '',
            'text': '',
            'color': ''
        }


# Test function
if __name__ == "__main__":
    # Test cases
    test_products = [
        {
            'title': 'Handmade Bamboo Basket',
            'description': 'Eco-friendly handwoven bamboo basket made by local artisans using traditional methods'
        },
        {
            'title': 'Ceramic Coffee Mug',
            'description': 'Hand-thrown pottery mug made from natural clay'
        },
        {
            'title': 'Plastic Storage Box',
            'description': 'Mass-produced synthetic storage container'
        }
    ]
    
    print("=" * 70)
    print("Sustainability Classification Tests")
    print("=" * 70)
    
    for product in test_products:
        print(f"\nProduct: {product['title']}")
        print(f"Description: {product['description']}")
        
        result = classify_product_sustainability(
            product['title'],
            product['description']
        )
        
        print(f"\n🎯 Result:")
        print(f"  Sustainable: {result['is_sustainable']}")
        print(f"  Score: {result['score']}/100")
        print(f"  Text Score: {result['text_score']}")
        print(f"  Image Score: {result['image_score']}")
        print(f"  Reasons:")
        for reason in result['reasons']:
            print(f"    • {reason}")
        print(f"  Keywords: {', '.join(result['keywords_found'][:5])}")
        print("-" * 70)
