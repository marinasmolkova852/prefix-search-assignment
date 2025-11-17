# utils.py
from transliterate import translit

# Простейшая функция исправления раскладки
LAYOUT_MAP = str.maketrans(
    "йцукенгшщзхъфывапролджэячсмитьбю",
    "qwertyuiop[]asdfghjkl;'zxcvbnm,."
)

def fix_layout(text: str) -> str:
    """
    Преобразует текст с неправильной раскладкой клавиатуры.
    """
    return text.translate(LAYOUT_MAP)

def transliterate_text(text: str, reversed: bool = False) -> str:
    """
    Транслитерирует текст c кириллицы на латиницу или обратно.
    """
    try:
        return translit(text, 'ru', reversed=reversed)
    except Exception:
        return text


def prepare_query(query: str) -> str:
    """
    Применяет исправление раскладки + транслитерацию + lowercase.
    """
    text = fix_layout(query)
    text = transliterate_text(text)
    return text.lower()
