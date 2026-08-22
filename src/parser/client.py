import logging
import httpx
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Origin': 'https://www.wildberries.ru',
    'Referer': 'https://www.wildberries.ru/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


def _get_basket_number(vol: int) -> str:
    if 0 <= vol <= 143:
        return "basket-01"
    elif 144 <= vol <= 287:
        return "basket-02"
    elif 288 <= vol <= 431:
        return "basket-03"
    elif 432 <= vol <= 719:
        return "basket-04"
    elif 720 <= vol <= 1007:
        return "basket-05"
    elif 1008 <= vol <= 1061:
        return "basket-06"
    elif 1062 <= vol <= 1175:
        return "basket-07"
    elif 1176 <= vol <= 1331:
        return "basket-08"
    elif 1332 <= vol <= 1451:
        return "basket-09"
    elif 1452 <= vol <= 1607:
        return "basket-10"
    elif 1608 <= vol <= 1655:
        return "basket-11"
    elif 1656 <= vol <= 1919:
        return "basket-12"
    elif 1920 <= vol <= 2045:
        return "basket-13"
    elif 2046 <= vol <= 2189:
        return "basket-14"
    elif 2190 <= vol <= 2405:
        return "basket-15"
    elif 2406 <= vol <= 2621:
        return "basket-16"
    elif 2622 <= vol <= 2837:
        return "basket-17"
    elif 2838 <= vol <= 3053:
        return "basket-18"
    elif 3054 <= vol <= 3269:
        return "basket-19"
    elif 3270 <= vol <= 3485:
        return "basket-20"
    elif 3486 <= vol <= 3701:
        return "basket-21"
    elif 3702 <= vol <= 3917:
        return "basket-22"
    elif 3918 <= vol <= 4133:
        return "basket-23"
    elif 4134 <= vol <= 4349:
        return "basket-24"
    elif 4350 <= vol <= 4565:
        return "basket-25"
    else:
        return "basket-26"


async def get_product_info(nm_id: int, max_retries: int = 3) -> dict | None:
    vol = nm_id // 100000
    part = nm_id // 1000
    basket = _get_basket_number(vol)

    image_url = f"https://{basket}.wbbasket.ru/vol{vol}/part{part}/images/big/1.webp"

    # Список эндпоинтов от самого надежного для артикулов к запасному
    urls = [
        f"https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-1257786&nm={nm_id}",
        f"https://search.wb.ru/exactmatch/ru/common/v18/search?appType=1&curr=rub&dest=-1257786&query={nm_id}&resultset=catalog"
    ]

    for url in urls:
        for attempt in range(max_retries):
            async with httpx.AsyncClient(headers=HEADERS, timeout=10.0, follow_redirects=True) as client:
                try:
                    response = await client.get(url)

                    if response.status_code == 200:
                        data = response.json()
                        products = data.get("data", {}).get("products", [])
                        if not products:
                            products = data.get("products", [])

                        if products:
                            p = products[0]
                            title = p.get("name")

                            price = None
                            sizes = p.get("sizes", [{}])
                            if sizes:
                                price_raw = sizes[0].get("price", {}).get("product", 0)
                                if price_raw:
                                    price = int(price_raw) // 100

                            if not price:
                                price_raw = p.get("salePriceU") or p.get("priceU")
                                if price_raw:
                                    price = int(price_raw) // 100

                            if title and price:
                                logger.info(f"✅ Успешно получен товар {nm_id} через {url.split('?')[0]}")
                                return {
                                    "nm_id": nm_id,
                                    "title": title,
                                    "price": price,
                                    "image_url": image_url,
                                }

                        # Если 200 OK, но товаров нет (как в случае с product-redirect),
                        # прерываем цикл попыток для ЭТОГО url и переходим к следующему url
                        logger.warning(f"⚠️ Ответ 200, но товар не найден по ссылке {url.split('?')[0]}")
                        break

                    elif response.status_code == 429:
                        wait_time = 2 ** attempt
                        logger.warning(
                            f"⚠️ 429 Too Many Requests. Ждем {wait_time} сек (Попытка {attempt + 1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                        continue

                    else:
                        logger.error(f"❌ Статус {response.status_code} при запросе к {url.split('?')[0]}")
                        break

                except Exception as e:
                    logger.error(f"❌ Ошибка соединения: {e}")
                    break

    logger.error(f"❌ Не удалось распарсить товар {nm_id} всеми доступными способами.")
    return None