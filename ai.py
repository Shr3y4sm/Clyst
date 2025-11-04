import os
import json
import base64
import mimetypes
import requests
import re
from typing import List, Dict, Any, Optional

try:
    import google.generativeai as genai
except Exception:
    genai = None


def generate_copy_suggestions(content_type: str, prompt: str = '', description: str = '', 
                            image_url: str = '', image_base64: str = '', image_mime: str = '',
                            api_key: str = None) -> Dict[str, Any]:
    """
    Generate title/description suggestions based on provided prompt/description and optional image.
    Returns a dictionary with 'ok' status and either 'suggestions' or 'error'.
    """
    try:
        content_type = content_type.lower()
        prompt = prompt.strip()
        description = description.strip()
        image_url = image_url.strip()
        image_present = bool(image_url or image_base64)

        # Require image presence for generation to align with UX
        if not image_present:
            return {
                'ok': False,
                'error': 'Image is required (URL or file) to generate suggestions.'
            }

        # If Gemini is configured, use it; otherwise fallback to simple stub
        if genai and api_key and api_key != "your_gemini_api_key_here":
            try:
                genai.configure(api_key=api_key)
                # Encourage variation and ask for JSON output directly
                model = genai.GenerativeModel(
                    model_name='gemini-2.5-pro',
                    generation_config={
                        'temperature': 0.9,
                        'top_p': 0.95,
                        'response_mime_type': 'application/json'
                    }
                )

                # Prepare image bytes
                image_part = None
                if image_base64:
                    try:
                        image_bytes = base64.b64decode(image_base64)
                        mime_type = image_mime or 'image/jpeg'
                        image_part = {
                            'mime_type': mime_type,
                            'data': image_bytes
                        }
                    except Exception:
                        image_part = None
                elif image_url:
                    try:
                        # Best-effort fetch; limit size
                        resp = requests.get(image_url, timeout=10)
                        resp.raise_for_status()
                        content = resp.content
                        # Basic size guard (16MB already enforced server-wide)
                        mime_type = resp.headers.get('Content-Type') or mimetypes.guess_type(image_url)[0] or 'image/jpeg'
                        image_part = {
                            'mime_type': mime_type,
                            'data': content
                        }
                    except Exception:
                        image_part = None

                user_goal = 'product listing' if content_type == 'product' else 'social post'
                guidance = prompt or ''
                base_text = description or ''
                instruction = (
                    "You are a creative copy assistant for artists. "
                    f"Given an artwork image and optional context for a {user_goal}, "
                    "generate exactly 3 varied suggestions as strict JSON array under key suggestions, "
                    "each item with keys 'title' and 'description'. Keep titles under 60 chars; descriptions under 280 chars. "
                    "Return ONLY JSON with shape: {\"suggestions\":[{\"title\":\"...\",\"description\":\"...\"}, ...]}"
                )

                # Put image first to ground the response in the artwork
                parts: List[Any] = []
                if image_part:
                    parts.append(image_part)
                parts.append(instruction)
                if guidance:
                    parts.append(f"Prompt: {guidance}")
                if base_text:
                    parts.append(f"Context: {base_text}")

                result = model.generate_content(parts)

                # Robustly extract text
                text = ''
                try:
                    text = (getattr(result, 'text', '') or '').strip()
                except Exception:
                    text = ''
                if not text:
                    try:
                        for cand in getattr(result, 'candidates', []) or []:
                            content = getattr(cand, 'content', None)
                            for p in getattr(content, 'parts', []) or []:
                                pt = getattr(p, 'text', None)
                                if pt:
                                    text += str(pt)
                        text = text.strip()
                    except Exception:
                        text = ''
                suggestions = []
                try:
                    # If extra text surrounds JSON, isolate the outermost JSON object
                    candidate = text
                    if '{' in text and '}' in text:
                        candidate = text[text.find('{'): text.rfind('}') + 1]
                    parsed = json.loads(candidate)
                    for item in (parsed.get('suggestions') or [])[:3]:
                        title = str(item.get('title', '')).strip()
                        desc = str(item.get('description', '')).strip()
                        if title and desc:
                            suggestions.append({'title': title, 'description': desc})
                except Exception:
                    # Fallback: derive multiple variants from lines
                    lines = [ln.strip('- •\t ') for ln in (text or '').split('\n') if ln.strip()]
                    if lines:
                        for i, ln in enumerate(lines[:3]):
                            suggestions.append({
                                'title': (ln[:60] or 'Artwork Suggestion'),
                                'description': (ln[:280] or 'A unique piece blending technique and emotion.')
                            })

                if not suggestions:
                    # Final fallback simple templates
                    base_context = (prompt or description or 'artwork').strip() or 'artwork'
                    is_product = content_type == 'product'
                    titles = [
                        f"{base_context.capitalize()}: A Visual Story",
                        f"{base_context.capitalize()} — Limited Edition",
                        f"The Essence of {base_context.capitalize()}"
                    ]
                    descs = [
                        "Handcrafted piece with meticulous detail.",
                        "Original work. Premium materials, gallery-ready finish.",
                        "Expressive composition. Ships safely, ready to display."
                    ] if is_product else [
                        "An exploration through texture, light, and color.",
                        "Captures movement and mood with layered technique.",
                        "A contemplative blend of technique and emotion."
                    ]
                    suggestions = [{ 'title': titles[i], 'description': descs[i]} for i in range(3)]

                return {'ok': True, 'suggestions': suggestions}
            except Exception as e:
                return {'ok': False, 'error': f'Gemini error: {str(e)}'}

        # Fallback stub generation when Gemini not configured
        base_context = (prompt or description or 'artwork').strip() or 'artwork'
        titles = [
            f"{base_context.capitalize()}: A Visual Story",
            f"{base_context.capitalize()} — Limited Edition",
            f"The Essence of {base_context.capitalize()}"
        ]
        is_product = content_type == 'product'
        descriptions = [
            "Handcrafted piece with meticulous detail.",
            "Original work. Premium materials, gallery-ready finish.",
            "Expressive composition. Ships safely, ready to display."
        ] if is_product else [
            "An exploration through texture, light, and color.",
            "Captures movement and mood with layered technique.",
            "A contemplative blend of technique and emotion."
        ]
        suggestions = [{'title': titles[i], 'description': descriptions[i]} for i in range(3)]
        return {'ok': True, 'suggestions': suggestions}
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def translate_listing(content_type: str, title: str = '', description: str = '', 
                     target_lang: str = '', locale: str = '', source_lang: str = '',
                     api_key: str = None) -> Dict[str, Any]:
    """
    Translate a listing's title/description into a target language and suggest SEO phrases.
    Returns a dictionary with 'ok' status and either translated content or 'error'.
    """
    try:
        content_type = content_type.lower()
        title = title.strip()
        description = description.strip()
        target_lang = target_lang.strip().lower()
        locale = locale.strip().lower()
        source_lang = source_lang.strip().lower()

        if not target_lang:
            return {'ok': False, 'error': 'target_lang is required'}
        if not (title or description):
            return {'ok': False, 'error': 'Provide title or description to translate'}

        # Lightweight source language heuristic if not provided (supports many scripts)
        def guess_lang(sample_text: str) -> str:
            try:
                s = sample_text or ''
                if re.search(r"[\u0900-\u097F]", s):  # Devanagari (hi, mr, ne)
                    return 'hi'
                if re.search(r"[\u0980-\u09FF]", s):  # Bengali
                    return 'bn'
                if re.search(r"[\u0A00-\u0A7F]", s):  # Gurmukhi
                    return 'pa'
                if re.search(r"[\u0A80-\u0AFF]", s):  # Gujarati
                    return 'gu'
                if re.search(r"[\u0B00-\u0B7F]", s):  # Oriya/Odia
                    return 'or'
                if re.search(r"[\u0B80-\u0BFF]", s):  # Tamil
                    return 'ta'
                if re.search(r"[\u0C00-\u0C7F]", s):  # Telugu
                    return 'te'
                if re.search(r"[\u0C80-\u0CFF]", s):  # Kannada
                    return 'kn'
                if re.search(r"[\u0D00-\u0D7F]", s):  # Malayalam
                    return 'ml'
                if re.search(r"[\u0600-\u06FF]", s):  # Arabic script
                    return 'ar'
                if re.search(r"[\u3040-\u309F\u30A0-\u30FF]", s):  # Hiragana/Katakana
                    return 'ja'
                if re.search(r"[\u4E00-\u9FFF\u3400-\u4DBF]", s):  # CJK Han
                    return 'zh'
                if re.search(r"[\uAC00-\uD7AF]", s):  # Hangul
                    return 'ko'
                if re.search(r"[\u0400-\u04FF]", s):  # Cyrillic
                    return 'ru'
                if re.search(r"[\u0370-\u03FF]", s):  # Greek
                    return 'el'
                if re.search(r"[\u0590-\u05FF]", s):  # Hebrew
                    return 'he'
            except Exception:
                pass
            return ''

        if not source_lang:
            source_lang = guess_lang((title + "\n" + description).strip())

        if genai and api_key and api_key != "your_gemini_api_key_here":
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name='gemini-2.5-pro',
                    generation_config={
                        'temperature': 0.3,
                        'top_p': 0.8,
                        'response_mime_type': 'application/json'
                    }
                )
                instruction = (
                    "You are a localization assistant for an art marketplace. "
                    f"Translate from {source_lang or 'auto-detected'} to {target_lang}. "
                    "Translate naturally and fluently while staying faithful to the original meaning. "
                    "Do not add new information or marketing fluff. Preserve names and intent. "
                    "If the source already matches the target language, return it as-is. "
                    f"Translate the following {content_type} listing into the target language. "
                    "Return ONLY JSON with keys: title, description, seo_phrases (array of 6 short phrases suitable for search/hashtags in the target locale). "
                    "No emojis."
                )
                user_json = json.dumps({
                    'title': title,
                    'description': description,
                    'target_lang': target_lang,
                    'source_lang': source_lang,
                    'locale': locale,
                })
                result = model.generate_content([instruction, f"INPUT:\n{user_json}"])
                out_text = ''
                try:
                    out_text = (getattr(result, 'text', '') or '').strip()
                except Exception:
                    out_text = ''
                if not out_text:
                    try:
                        for cand in getattr(result, 'candidates', []) or []:
                            content = getattr(cand, 'content', None)
                            for p in getattr(content, 'parts', []) or []:
                                pt = getattr(p, 'text', None)
                                if pt:
                                    out_text += str(pt)
                        out_text = out_text.strip()
                    except Exception:
                        out_text = ''
                parsed = {}
                try:
                    candidate = out_text
                    if '{' in out_text and '}' in out_text:
                        candidate = out_text[out_text.find('{'): out_text.rfind('}') + 1]
                    parsed = json.loads(candidate)
                except Exception:
                    parsed = {}
                tr_title = str(parsed.get('title') or title).strip()
                tr_desc = str(parsed.get('description') or description).strip()
                seo_phrases = parsed.get('seo_phrases') or []
                # Ensure list of strings
                if not isinstance(seo_phrases, list):
                    seo_phrases = []
                seo_phrases = [str(s).strip() for s in seo_phrases if str(s).strip()]
                return {'ok': True, 'title': tr_title, 'description': tr_desc, 'seo_phrases': seo_phrases[:8]}
            except Exception as e:
                return {'ok': False, 'error': f'Gemini error: {str(e)}'}

        # Fallback stub translation when Gemini not configured
        # Simple placeholder to show multi-language UI works without external API.
        lang_prefix = target_lang if target_lang else 'xx'
        def stub_translate(text_in: str) -> str:
            if not text_in:
                return ''
            return f"[{lang_prefix}] {text_in}"
        tr_title = stub_translate(title)
        tr_desc = stub_translate(description)
        # Very basic seo generation from source words
        base_words = []
        base_words.extend((title or '').split())
        base_words.extend((description or '').split())
        base_words = [w.strip('#,.;:!()[]{}"'"'" ).lower() for w in base_words if len(w) > 3][:12]
        seo_phrases = list({f"{lang_prefix}-{w}" for w in base_words})
        seo_phrases = seo_phrases[:8]
        return {'ok': True, 'title': tr_title, 'description': tr_desc, 'seo_phrases': seo_phrases}
    except Exception as e:
        return {'ok': False, 'error': str(e)}

def generate_portfolio_narrative(artist_name: str, posts: List[Dict], products: List[Dict]) -> str:
    """
    Generate a basic portfolio narrative as fallback.
    """
    if not posts and not products:
        return f"Welcome to {artist_name}'s creative space. This collection is just beginning to take shape."
    
    total_works = len(posts) + len(products)
    posts_count = len(posts)
    products_count = len(products)
    
    return f"Welcome to {artist_name}'s artistic journey, a collection that weaves together {total_works} unique pieces into a compelling narrative of creativity and expression. This collection includes {posts_count} community-shared works that showcase the artist's creative process, alongside {products_count} carefully crafted pieces available for acquisition. Together, these works form a cohesive narrative that invites viewers to explore {artist_name}'s unique perspective and artistic voice."


def generate_enhanced_portfolio_narrative(artist_name: str, posts: List[Dict], products: List[Dict], user_location: str = None) -> str:
    """
    Generate an AI-powered portfolio narrative using Google Gemini API.
    Analyzes all artwork and creates a compelling story connecting the works.
    """
    
    if not posts and not products:
        return f"Welcome to {artist_name}'s creative space. This collection is just beginning to take shape."
    
    try:
        # Import Gemini here to avoid import errors if not available
        import google.generativeai as genai
        from config import GEMINI_API_KEY
        
        # Check if Gemini is available and configured
        api_key = GEMINI_API_KEY
        if not genai or not api_key or api_key == "your_gemini_api_key_here":
            return generate_portfolio_narrative(artist_name, posts, products)
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name='gemini-2.5-pro',
            generation_config={
                'temperature': 0.7,
                'top_p': 0.9,
                'max_output_tokens': 500,
            }
        )
        
        # Prepare comprehensive data for AI analysis
        all_works = []
        
        # Process posts
        for post in posts:
            work_data = {
                'type': 'community_post',
                'title': post.get('post_title', ''),
                'description': post.get('post_description', ''),
                'created_at': post.get('created_at', ''),
                'media_url': post.get('media_url', '')
            }
            all_works.append(work_data)
        
        # Process products
        for product in products:
            work_data = {
                'type': 'marketplace_product',
                'title': product.get('title', ''),
                'description': product.get('description', ''),
                'price': product.get('price', ''),
                'created_at': product.get('created_at', ''),
                'img_url': product.get('img_url', '')
            }
            all_works.append(work_data)
        
        # Create AI prompt
        location_context = f" from {user_location}" if user_location else ""
        works_summary = f"Total works: {len(all_works)} (Posts: {len(posts)}, Products: {len(products)})"
        
        prompt = f"""
You are an expert art curator and storyteller. Analyze this artist's portfolio and create a compelling "About This Collection" narrative that connects their works into a cohesive artistic story.

ARTIST: {artist_name}{location_context}
{works_summary}

ARTWORKS TO ANALYZE:
{json.dumps(all_works, indent=2)}

Create a narrative that:
1. Welcomes visitors to the artist's creative journey
2. Identifies key themes, styles, and artistic evolution
3. Connects the works into a meaningful story
4. Highlights the balance between community posts and marketplace products
5. Invites viewers to explore the collection
6. Uses engaging, professional language suitable for an art marketplace
7. Keeps it concise but compelling (2-3 paragraphs max)

Focus on the artistic themes, creative evolution, and the story these works tell together. Make it feel personal and inspiring.
"""
        
        # Generate AI response
        response = model.generate_content(prompt)
        narrative = response.text.strip()
        
        # Fallback if AI response is empty or too short
        if not narrative or len(narrative) < 50:
            return generate_portfolio_narrative(artist_name, posts, products)
        
        return narrative
        
    except Exception as e:
        # If AI fails, return basic narrative
        print(f"AI portfolio narrative generation failed: {e}")
        return generate_portfolio_narrative(artist_name, posts, products)


def chat_with_product(question: str, product_data: Dict[str, Any], api_key: str = None) -> Dict[str, Any]:
    """
    Hybrid chatbot for product Q&A using 3-layer approach:
    1. Pattern matching for common questions
    2. Product-specific extraction from description
    3. Gemini AI fallback with safety rules
    
    Returns: {'answer': str, 'source': 'pattern|extraction|ai', 'suggestions': list}
    """
    
    question_lower = question.lower().strip()
    
    # Layer 1: Pattern Matching for Common Questions
    common_patterns = {
        'shipping': {
            'keywords': ['ship', 'deliver', 'shipping', 'delivery', 'how long', 'when will'],
            'answer': "Shipping times vary by location. Please contact the seller for specific delivery estimates to your area.",
            'suggestions': ['What materials is this made from?', 'Can I customize this?', 'Is this available in other sizes?']
        },
        'materials': {
            'keywords': ['material', 'made of', 'made from', 'fabric', 'wood', 'metal', 'what is it'],
            'answer': None,  # Will extract from description
            'suggestions': ['How much does shipping cost?', 'Can I customize this?', 'When will it arrive?']
        },
        'customize': {
            'keywords': ['customize', 'customiz', 'custom', 'personalize', 'modify', 'change'],
            'answer': "Customization options depend on the artisan. Please use the 'Contact Seller' button to discuss your specific requirements.",
            'suggestions': ['What materials is this made from?', 'How long will delivery take?', 'Is this handmade?']
        },
        'price': {
            'keywords': ['price', 'cost', 'how much', 'expensive', 'cheap', 'discount', 'payment'],
            'answer': f"The current price is Rs.{product_data.get('price', 'N/A')}. For any special offers or bulk discounts, please contact the seller directly.",
            'suggestions': ['What materials is this made from?', 'How long will shipping take?', 'Can I customize this?']
        },
        'size': {
            'keywords': ['size', 'dimension', 'how big', 'how small', 'measurement', 'height', 'width'],
            'answer': None,  # Will extract from description
            'suggestions': ['What materials is this made from?', 'Can I customize the size?', 'How much does shipping cost?']
        },
        'handmade': {
            'keywords': ['handmade', 'hand made', 'handcraft', 'artisan', 'craft'],
            'answer': "This is a handcrafted artisan product. For details about the creation process, please check the description or contact the seller.",
            'suggestions': ['What materials is this used?', 'Can I see more from this artist?', 'How long will delivery take?']
        },
    }
    
    # Check pattern match
    matched_pattern = None
    for pattern_name, pattern_data in common_patterns.items():
        if any(keyword in question_lower for keyword in pattern_data['keywords']):
            matched_pattern = pattern_data
            break
    
    # Layer 2: Product-Specific Extraction
    def extract_from_description(keywords, description):
        """Extract relevant information from product description"""
        if not description:
            return None
        
        desc_lower = description.lower()
        sentences = [s.strip() for s in description.split('.') if s.strip()]
        
        # Find sentences containing keywords
        relevant_sentences = []
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                relevant_sentences.append(sentence)
        
        if relevant_sentences:
            return ' '.join(relevant_sentences[:2])  # Return up to 2 relevant sentences
        return None
    
    # If pattern matched and requires extraction
    if matched_pattern and matched_pattern['answer'] is None:
        description = product_data.get('description', '')
        keywords = matched_pattern['keywords']
        extracted = extract_from_description(keywords, description)
        
        if extracted:
            return {
                'answer': extracted + "\n\n💬 Need more details? Use the 'Contact Seller' button below.",
                'source': 'extraction',
                'suggestions': matched_pattern['suggestions']
            }
    
    # If pattern matched with predefined answer
    if matched_pattern and matched_pattern['answer']:
        return {
            'answer': matched_pattern['answer'],
            'source': 'pattern',
            'suggestions': matched_pattern['suggestions']
        }
    
    # Layer 3: Gemini AI Fallback
    if genai and api_key and api_key != "your_gemini_api_key_here":
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash-lite',
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.95,
                    'max_output_tokens': 300,
                }
            )
            
            # Build safe context
            context = f"""
You are a helpful product assistant for an artisan marketplace. Answer questions about this product accurately and helpfully.

PRODUCT INFORMATION:
- Title: {product_data.get('title', 'N/A')}
- Price: Rs.{product_data.get('price', 'N/A')}
- Artist: {product_data.get('artist_name', 'N/A')}
- Description: {product_data.get('description', 'No description available')}

STRICT RULES:
1. NEVER make promises about payment, refunds, returns, or guarantees
2. NEVER provide seller's contact information
3. If you're not certain, say "Please contact the seller for accurate information"
4. Keep answers concise (2-3 sentences max)
5. Always be helpful and polite
6. Focus only on the product information provided

USER QUESTION: {question}

Provide a helpful answer based on the product information. If the answer isn't clear from the description, politely suggest contacting the seller.
"""
            
            response = model.generate_content(context)
            ai_answer = response.text.strip()
            
            # Add contact seller nudge
            if any(word in ai_answer.lower() for word in ['contact', 'ask', 'unclear', 'not sure', 'depends']):
                ai_answer += "\n\n💬 For specific details, please use the 'Contact Seller' button below."
            
            return {
                'answer': ai_answer,
                'source': 'ai',
                'suggestions': [
                    'Tell me more about the materials',
                    'How long will shipping take?',
                    'Can this be customized?',
                    'Is this handmade?'
                ]
            }
            
        except Exception as e:
            print(f"AI chat failed: {e}")
            # Fallback to generic response
            pass
    
    # Final fallback if all layers fail
    return {
        'answer': f"I'd be happy to help! For detailed information about \"{product_data.get('title', 'this product')}\", please contact the seller directly using the 'Contact Seller' button below. They can provide specific details about materials, shipping, customization, and more.",
        'source': 'fallback',
        'suggestions': [
            'What materials is this made from?',
            'How long will delivery take?',
            'Can I customize this?',
            'Is this handmade?'
        ]
    }


def generate_artisan_insights(artisan_data: Dict[str, Any], api_key: str = None) -> Dict[str, Any]:
    """
    Generate AI-powered insights for artisans to improve their art and marketing.
    
    Args:
        artisan_data: Dictionary containing:
            - products: list of dicts with title, description, price, views, reviews, avg_rating
            - posts: list of dicts with title, likes, comments
            - revenue: dict with total, paid, items_sold, total_orders
            - top_products: list of top performing products
            - engagement: dict with total_likes, total_comments, total_reviews
        api_key: Groq API key
    
    Returns:
        Dict with 'ok' status and either 'insights' or 'error'
    """
    try:
        if not api_key or api_key == "your_groq_api_key_here":
            return {
                'ok': False,
                'error': 'Groq API key not configured. Please add GROQ_API_KEY to your environment variables.'
            }

        # Prepare context from artisan data
        products = artisan_data.get('products', [])
        posts = artisan_data.get('posts', [])
        revenue = artisan_data.get('revenue', {})
        top_products = artisan_data.get('top_products', [])
        engagement = artisan_data.get('engagement', {})

        # Build prompt for Groq
        prompt = f"""You are an expert business advisor for artisan marketplaces. Analyze the following data and provide actionable insights.

ARTIST PERFORMANCE DATA:

Products ({len(products)} total):
"""
        # Add product details
        for i, p in enumerate(products[:10], 1):  # Limit to top 10 for token efficiency
            prompt += f"{i}. {p.get('title', 'Untitled')} - ₹{p.get('price', 0)} | Views: {p.get('views', 0)} | Reviews: {p.get('reviews', 0)} | Avg Rating: {p.get('avg_rating', 0):.1f}/5\n"
        
        if len(products) > 10:
            prompt += f"... and {len(products) - 10} more products\n"

        prompt += f"\nPosts ({len(posts)} total):\n"
        for i, p in enumerate(posts[:5], 1):  # Top 5 posts
            prompt += f"{i}. {p.get('title', 'Untitled')} | Likes: {p.get('likes', 0)} | Comments: {p.get('comments', 0)}\n"

        prompt += f"""
Revenue & Sales:
- Total Orders: {revenue.get('total_orders', 0)}
- Items Sold: {revenue.get('items_sold', 0)}
- Total Revenue: ₹{revenue.get('total', 0):.2f}
- Paid Revenue: ₹{revenue.get('paid', 0):.2f}

Engagement:
- Total Likes: {engagement.get('total_likes', 0)}
- Total Comments: {engagement.get('total_comments', 0)}
- Total Reviews: {engagement.get('total_reviews', 0)}

Top Performing Products:
"""
        for i, tp in enumerate(top_products[:3], 1):
            prompt += f"{i}. {tp.get('title', 'Untitled')} - {tp.get('metric', 'N/A')}\n"

        prompt += """
TASK: Provide specific, actionable insights in these 4 categories:

1. Product Optimization: How to improve product listings (titles, descriptions, pricing, photography)
2. Marketing Strategy: Content ideas, social media tactics, audience engagement
3. Pricing Strategy: Pricing analysis and recommendations
4. Growth Opportunities: New product ideas, expansion strategies

Return ONLY a valid JSON object with this exact structure:
{
  "product_optimization": ["insight 1", "insight 2", "insight 3"],
  "marketing_strategy": ["insight 1", "insight 2", "insight 3"],
  "pricing_strategy": ["insight 1", "insight 2", "insight 3"],
  "growth_opportunities": ["insight 1", "insight 2", "insight 3"]
}

Each insight should be 1-2 sentences, specific, and actionable. Base recommendations on the actual data provided.
"""

        # Call Groq API
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'llama-3.3-70b-versatile',  # Fast, high-quality model (updated Nov 2024)
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert business advisor for artisan marketplaces. Provide actionable, data-driven insights in valid JSON format only.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.7,
            'max_tokens': 1500,
            'response_format': {'type': 'json_object'}
        }

        try:
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
        except requests.exceptions.Timeout:
            return {
                'ok': False,
                'error': 'Request to Groq API timed out after 30 seconds. Please try again.'
            }
        except requests.exceptions.ConnectionError:
            return {
                'ok': False,
                'error': 'Could not connect to Groq API. Please check your internet connection.'
            }
        
        if response.status_code != 200:
            error_msg = f'Groq API error: {response.status_code}'
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_msg += f' - {error_data["error"].get("message", response.text)}'
            except:
                error_msg += f' - {response.text[:200]}'
            
            return {
                'ok': False,
                'error': error_msg
            }

        result = response.json()
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        if not content:
            return {
                'ok': False,
                'error': 'Empty response from Groq API'
            }

        # Parse JSON response
        try:
            insights_data = json.loads(content)
            
            # Validate structure
            required_keys = ['product_optimization', 'marketing_strategy', 'pricing_strategy', 'growth_opportunities']
            for key in required_keys:
                if key not in insights_data:
                    insights_data[key] = []
            
            return {
                'ok': True,
                'insights': insights_data
            }
        except json.JSONDecodeError as e:
            return {
                'ok': False,
                'error': f'Failed to parse AI response as JSON: {str(e)}'
            }

    except requests.exceptions.RequestException as e:
        return {
            'ok': False,
            'error': f'Network error calling Groq API: {str(e)}'
        }
    except Exception as e:
        return {
            'ok': False,
            'error': f'Unexpected error generating insights: {str(e)}'
        }


def find_similar_products_and_pricing(product_data: Dict[str, Any], marketplace_products: List[Dict[str, Any]], 
                                     api_key: str = None, include_external: bool = False) -> Dict[str, Any]:
    """
    Use AI to find similar products based on product characteristics (not just price).
    Optionally includes external market research.
    
    Args:
        product_data: Dict with title, description, price, category info
        marketplace_products: List of other products in local marketplace
        api_key: Groq API key
        include_external: Whether to search external sources (Amazon, eBay, etc.)
    
    Returns:
        Dict with 'ok' status and either 'analysis' or 'error'
    """
    try:
        if not api_key or api_key == "your_groq_api_key_here":
            return {
                'ok': False,
                'error': 'Groq API key not configured.'
            }

        # Build prompt for AI to analyze similarity and pricing
        prompt = f"""You are an expert in handcrafted products and competitive pricing analysis.

PRODUCT TO ANALYZE:
Title: {product_data.get('title', 'Unknown')}
Description: {product_data.get('description', 'No description')}
Price: ₹{product_data.get('price', 0)}

MARKETPLACE PRODUCTS:
"""
        # Add marketplace products
        for i, p in enumerate(marketplace_products[:20], 1):  # Limit to 20 for token efficiency
            prompt += f"{i}. {p.get('title', 'Unknown')} - ₹{p.get('price', 0)} | {p.get('artist_name', 'Unknown')}\n"
            if p.get('description'):
                prompt += f"   Description: {p.get('description')[:100]}...\n"

        if include_external:
            prompt += f"""

EXTERNAL MARKET RESEARCH TASK:
Based on the product title "{product_data.get('title', '')}" and description, suggest typical pricing for similar handcrafted products on:
- Amazon India (handmade/artisan sections)
- Etsy India
- Flipkart Handpicked
- Indian art marketplaces

Provide realistic price estimates based on your knowledge of these platforms.
"""

        prompt += """

ANALYSIS TASKS:
1. Identify the 5 most similar products from the marketplace based on:
   - Product type/category
   - Materials/craftsmanship
   - Target audience
   - Artistic style
   (NOT just price similarity - focus on actual product similarity)

2. Compare pricing of similar products

3. Provide competitive pricing recommendations"""

        if include_external:
            prompt += """

4. Research external market pricing for similar products"""

        prompt += """

Return ONLY a valid JSON object with this structure:
{
  "similar_products": [
    {
      "index": 1,
      "similarity_score": 95,
      "reason": "why this product is similar",
      "price_comparison": "higher/lower/similar"
    }
  ],
  "pricing_analysis": {
    "your_position": "premium/competitive/budget",
    "similar_avg_price": 1500.00,
    "recommendation": "specific pricing advice"
  }"""

        if include_external:
            prompt += """,
  "external_market": {
    "amazon_range": "₹1200-2000",
    "etsy_range": "₹1500-2500",
    "flipkart_range": "₹1000-1800",
    "recommendation": "how you compare to external markets"
  }"""

        prompt += """
}

Provide specific, actionable insights based on product characteristics and actual similarity.
"""

        # Call Groq API
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'llama-3.3-70b-versatile',
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert in handcrafted products, artisan markets, and competitive pricing analysis. Provide detailed, accurate analysis in valid JSON format.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.5,  # Lower temperature for more consistent analysis
            'max_tokens': 2000,
            'response_format': {'type': 'json_object'}
        }

        try:
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
        except requests.exceptions.Timeout:
            return {
                'ok': False,
                'error': 'Request timed out. Please try again.'
            }
        except requests.exceptions.ConnectionError:
            return {
                'ok': False,
                'error': 'Could not connect to AI service. Check internet connection.'
            }
        
        if response.status_code != 200:
            error_msg = f'AI API error: {response.status_code}'
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_msg += f' - {error_data["error"].get("message", response.text)}'
            except:
                error_msg += f' - {response.text[:200]}'
            
            return {
                'ok': False,
                'error': error_msg
            }

        result = response.json()
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        if not content:
            return {
                'ok': False,
                'error': 'Empty response from AI'
            }

        # Parse JSON response
        try:
            analysis_data = json.loads(content)
            
            return {
                'ok': True,
                'analysis': analysis_data
            }
        except json.JSONDecodeError as e:
            return {
                'ok': False,
                'error': f'Failed to parse AI response: {str(e)}'
            }

    except Exception as e:
        return {
            'ok': False,
            'error': f'Error analyzing products: {str(e)}'
        }


