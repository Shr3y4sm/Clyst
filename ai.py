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

