import re


def extract_nm_id(text: str) -> int | None:
    """
    Извлекает артикул (nm_id) из текста или ссылки Wildberries.
    Приоритетно ищет ID товара в пути /catalog/, игнорируя размеры и параметры.
    """
    if not text:
        return None

    # Ищем артикул строго после /catalog/
    catalog_match = re.search(r"catalog/(\d+)", text)
    if catalog_match:
        return int(catalog_match.group(1))

    # Если передана просто строка из цифр без ссылки
    clean_text = text.strip()
    if clean_text.isdigit():
        return int(clean_text)

    return None