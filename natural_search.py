import re
from typing import Optional, Dict, Any, List
def parse_search_query(query: str) -> Dict[str, Any]:
    """
    Very lightweight natural language parser for queries like:
    - "minimalist monochrome abstracts under ₹5k"
    - "blue portrait < 2000"
    - "landscape oil painting below 7500"
    Extracts:
      - keywords: list[str]
      - max_price: float | None
      - min_price: float | None
    """
    text = (query or '').lower().strip()
    if not text:
        return { 'keywords': [], 'max_price': None, 'min_price': None }

    # Normalize currency symbols and shorthand
    norm = text.replace('rs.', 'rs').replace('₹', 'rs ').replace('inr', 'rs').replace('rupees', 'rs')
    # remove thousand separators like 1,200
    norm = re.sub(r"(?<=\d),(?=\d)", "", norm)
    norm = re.sub(r"\s+", " ", norm)

    def parse_amount(raw_val: str) -> Optional[float]:
        raw = raw_val.strip().replace(' ', '')
        mult = 1.0
        if raw.endswith(('k', 'K')):
            mult = 1000.0
            raw = raw[:-1]
        elif raw.endswith(('m', 'M')):
            mult = 1_000_000.0
            raw = raw[:-1]
        try:
            return float(raw) * mult
        except Exception:
            return None

    min_price: Optional[float] = None
    max_price: Optional[float] = None

    # Price ranges: between X and Y, from X to Y, X - Y
    range_patterns = [
        r"(?:between|from)\s*rs?\.?\s*([\d]+\s*[kKmM]?)\s*(?:and|to|-)\s*rs?\.?\s*([\d]+\s*[kKmM]?)",
        r"(?:between|from)\s*([\d]+\s*[kKmM]?)\s*(?:and|to|-)\s*([\d]+\s*[kKmM]?)",
        r"rs?\.?\s*([\d]+\s*[kKmM]?)\s*-\s*rs?\.?\s*([\d]+\s*[kKmM]?)",
        r"\b([\d]+\s*[kKmM]?)\s*-\s*([\d]+\s*[kKmM]?)\b",
    ]
    for pat in range_patterns:
        m = re.search(pat, norm)
        if m:
            lo = parse_amount(m.group(1))
            hi = parse_amount(m.group(2))
            if lo is not None and hi is not None:
                min_price = min(lo, hi)
                max_price = max(lo, hi)
                norm = norm.replace(m.group(0), ' ')
                break

    # Max price constraints: under/below/less than/< <= up to
    price_patterns = [
        r"(?:under|below|less than|upto|up to)\s*rs?\.?\s*([\d]+\s*[kKmM]?)",
        r"(?:under|below|less than|upto|up to)\s*([\d]+\s*[kKmM]?)",
        r"[<≤]\s*rs?\.?\s*([\d]+\s*[kKmM]?)",
        r"[<≤]\s*([\d]+\s*[kKmM]?)",
        r"rs?\.?\s*([\d]+\s*[kKmM]?)\s*(?:or less|and below)"
    ]
    for pat in price_patterns:
        m = re.search(pat, norm)
        if m:
            max_price = parse_amount(m.group(1))
            norm = norm.replace(m.group(0), ' ')
            break

    # Min price constraints: above/over/greater than/> >= from
    min_price_patterns = [
        r"(?:above|over|greater than|more than|from)\s*rs?\.?\s*([\d]+\s*[kKmM]?)",
        r"(?:above|over|greater than|more than|from)\s*([\d]+\s*[kKmM]?)",
        r"[>≥]\s*rs?\.?\s*([\d]+\s*[kKmM]?)",
        r"[>≥]\s*([\d]+\s*[kKmM]?)",
        r"rs?\.?\s*([\d]+\s*[kKmM]?)\s*(?:or more|and above)"
    ]
    for pat in min_price_patterns:
        m = re.search(pat, norm)
        if m:
            parsed_val = parse_amount(m.group(1))
            if parsed_val is not None:
                if min_price is None or parsed_val > min_price:
                    min_price = parsed_val
            norm = norm.replace(m.group(0), ' ')
            break

    # Exact price: for/at/= 1000, "rs 1200"
    exact_patterns = [
        r"(?:for|at|price of|priced at)\s*rs?\.?\s*([\d]+\s*[kKmM]?)",
        r"(?:for|at|price of|priced at)\s*([\d]+\s*[kKmM]?)",
        r"[=]\s*rs?\.?\s*([\d]+\s*[kKmM]?)",
        r"[=]\s*([\d]+\s*[kKmM]?)",
        r"\brs\.?\s*([\d]+\s*[kKmM]?)\b"
    ]
    for pat in exact_patterns:
        m = re.search(pat, norm)
        if m:
            val = parse_amount(m.group(1))
            if val is not None:
                min_price = val
                max_price = val
            norm = norm.replace(m.group(0), ' ')
            break

    # Remove price cue words and symbols
    scrub = re.sub(r"\brs\b|\bprice\b|\bunder\b|\bbelow\b|\bless than\b|\bupto\b|\bup to\b|\babove\b|\bover\b|\bgreater than\b|\bmore than\b|\bfrom\b|\bbetween\b|\band\b|\bto\b|\bfor\b|\bat\b|[<≤>≥=]", " ", norm)

    # Tokenize keywords (keep simple words > 2 chars)
    tokens = [t for t in re.split(r"[^a-z0-9]+", scrub) if t and len(t) > 2]

    # Basic stopwords (keep color/style words intact)
    stop = { 'with', 'and', 'the', 'this', 'that', 'for', 'into', 'from', 'your', 'have', 'are', 'art', 'arts', 'between', 'over', 'under', 'below', 'above', 'less', 'more', 'than', 'upto', 'up', 'to', 'at', 'price', 'rs' }
    keywords = [t for t in tokens if t not in stop]

    return { 'keywords': keywords, 'max_price': max_price, 'min_price': min_price }