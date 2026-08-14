import httpx
from .schemas import WBResponse


async def get_product_info(nm_id: int) -> dict | None:
    """
    Асинхронно делает запрос к публичному API Wildberries
    и возвращает название, цену в рублях и ссылку на изображение товара.
    """
    url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={nm_id}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                # Валидация JSON ответа через Pydantic
                data = WBResponse.model_validate_json(response.text)
                if data.data.products:
                    prod = data.data.products[0]
                    return {
                        "nm_id": prod.id,
                        "title": prod.name,
                        "price": prod.salePriceU // 100,  # Переводим копейки в рубли
                        "image_url": f"https://basket-01.wbbasket.ru/vol{prod.id // 100000}/part{prod.id // 1000}/images/big/1.webp"
                    }
        except Exception as e:
            print(f"Ошибка парсинга WB: {e}")
    return None