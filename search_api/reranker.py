# search_api/reranker.py
import re
from difflib import SequenceMatcher
from transliterate import translit


def normalize(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    # транслитерация → русские буквы
    try:
        text = translit(text, "ru")
    except Exception:
        pass
    text = re.sub(r"[^a-zа-я0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def prefix_score(query: str, name: str) -> float:
    """Оценка префикса — насколько хорошо q совпадает с началом слова."""
    name = name.lower()
    query = query.lower()

    if name.startswith(query):
        return 1.0
    if query in name:
        return 0.6
    return 0.0


def fuzzy_score(q: str, text: str) -> float:
    """Fuzzy similarity."""
    return SequenceMatcher(None, q, text).ratio()


def category_bonus(hit, expected_category):
    """Если пользовательский store подразумевает категорию — усиливаем совпадение."""
    if not expected_category:
        return 0
    if hit.get("category") == expected_category:
        return 0.5
    return 0


def rerank_smart(query: str, hits, expected_category=None):
    """
    Комбинированный reranker:
    - нормализованный prefix score
    - fuzzy score
    - category/brand бусты
    """

    q_norm = normalize(query)

    scored = []
    for h in hits:
        name = normalize(h.get("name", ""))
        brand = normalize(h.get("brand", ""))

        score = 0

        # prefix
        score += prefix_score(q_norm, name) * 2.0

        # fuzzy name
        score += fuzzy_score(q_norm, name) * 1.0

        # fuzzy brand
        score += fuzzy_score(q_norm, brand) * 0.8

        # category bonus (если магазин Store C/B/E/F → подсказывает категорию)
        score += category_bonus(h, expected_category)

        scored.append((score, h))

    # сортировка по убыванию
    scored.sort(key=lambda x: x[0], reverse=True)

    return [h for score, h in scored]

