import re

def extract_nm_id(text: str) -> int | None:
    """
    Извлекает артикул (nm_id) из текста.
    Работает как с простым текстом "12345678", так и с ссылками вида:
    https://www.wildberries.ru/catalog/12345678/detail.aspx
    """
    match = re.search(r'(?:catalog/)?(\d{6,12})', text)
    if match:
        return int(match.group(1))
    return None