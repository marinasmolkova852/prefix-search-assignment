# search_api/reranker_smart.py
import re
from typing import List, Dict

# Транслитерация и раскладка
CYR_TO_LAT = str.maketrans(
    "абвгдеёжзийклмнопрстуфхцчшщьыэюя",
    "abvgdeezhziyklmnoprstufhtschshsh'yeiuya"
)
QWERTY_TO_YCUKEN = str.maketrans(
    "qwertyuiop[]asdfghjkl;zxcvbnm,./",
    "йцукенгшщзхъфывапролджэячсмитьбю"
)

def normalize(text: str) -> str:
    text = text.lower()
    text = text.translate(CYR_TO_LAT)
    text = text.translate(QWERTY_TO_YCUKEN)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_numbers(text: str) -> List[int]:
    return [int(n) for n in re.findall(r"\d+", text)]

def score_item(query: str, item: Dict, expected_category: str = None) -> float:
    score = 0.0
    norm_query = normalize(query)
    text_fields = f"{item.get('name','')} {item.get('keywords','')}"
    norm_text = normalize(text_fields)
    query_words = norm_query.split()

    for w in query_words:
        if w in norm_text:
            score += 2.0
        elif len(w) <= 3 and norm_text.startswith(w):
            score += 1.0

    if expected_category and item.get("category") == expected_category:
        score += 3.0

    brand = item.get("brand","")
    if normalize(brand) in norm_text:
        score += 2.0

    query_nums = extract_numbers(norm_query)
    for key in ["weight", "package_size"]:
        val = item.get(key)
        if val is not None:
            for qn in query_nums:
                if abs(qn - val) <= 1:
                    score += 1.5

    for w in query_words:
        if norm_text.startswith(w):
            score += 1.0

    return score

def is_garbage(query: str, item: Dict, min_word_matches: int = 1) -> bool:
    """
    Фильтр «мусорных» результатов:
    - должно совпадать хотя бы min_word_matches слов из запроса
    - если указан expected_category, категория должна совпадать
    """
    norm_query = normalize(query)
    norm_text = normalize(f"{item.get('name','')} {item.get('keywords','')}")
    matches = sum(1 for w in norm_query.split() if w in norm_text)
    if matches < min_word_matches:
        return True
    return False

def rerank_smart(query: str, results: List[Dict], expected_category: str = None) -> List[Dict]:
    """
    Умный reranker с фильтром «мусорных» результатов:
    - boost по префиксам, числам, бренду, категории
    - отбрасывает результаты, не совпадающие хотя бы частично с запросом
    """
    filtered = [r for r in results if not is_garbage(query, r)]
    scored = [(score_item(query, r, expected_category), r) for r in filtered]
    ranked = [r for s, r in sorted(scored, key=lambda x: x[0], reverse=True)]
    return ranked
