import httpx
import logging

# Настраиваем логирование, чтобы видеть ответы WB в терминале
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8",
    "Origin": "https://www.wildberries.ru",
    "Referer": "https://www.wildberries.ru/",
}


def _get_basket_number(vol: int) -> str:
    if vol <= 143:
        return "01"
    elif vol <= 287:
        return "02"
    elif vol <= 431:
        return "03"
    elif vol <= 719:
        return "04"
    elif vol <= 1007:
        return "05"
    elif vol <= 1061:
        return "06"
    elif vol <= 1115:
        return "07"
    elif vol <= 1169:
        return "08"
    elif vol <= 1313:
        return "09"
    elif vol <= 1601:
        return "10"
    elif vol <= 1655:
        return "11"
    elif vol <= 1919:
        return "12"
    elif vol <= 2045:
        return "13"
    elif vol <= 2189:
        return "14"
    elif vol <= 2405:
        return "15"
    elif vol <= 2621:
        return "16"
    elif vol <= 2837:
        return "17"
    elif vol <= 3053:
        return "18"
    elif vol <= 3269:
        return "19"
    elif vol <= 3485:
        return "20"
    elif vol <= 3701:
        return "21"
    else:
        return "22"


def _extract_price_from_product(prod: dict) -> int | None:
    raw_price = prod.get("salePriceU") or prod.get("priceU")

    if not raw_price and "extended" in prod:
        raw_price = prod["extended"].get("basicPriceU")

    if not raw_price and "sizes" in prod and isinstance(prod["sizes"], list):
        for size in prod["sizes"]:
            p_info = size.get("price")
            if isinstance(p_info, dict):
                raw_price = p_info.get("product") or p_info.get("total")
                if raw_price:
                    break

    if raw_price:
        return int(raw_price) // 100
    return None


async def get_product_info(nm_id: int) -> dict | None:
    vol = nm_id // 100000
    part = nm_id // 1000
    basket = _get_basket_number(vol)

    # Гео-зоны: Москва, Минск, Екатеринбург, Казахстан
    dest_list = [-1257786, -59202, -1113279, -1221148]

    info_cdn_url = f"https://basket-{basket}.wbbasket.ru/vol{vol}/part{part}/info/ru/card.json"
    image_url = f"https://basket-{basket}.wbbasket.ru/vol{vol}/part{part}/images/big/1.webp"

    title = None
    price = None

    async with httpx.AsyncClient(headers=HEADERS, timeout=15.0, follow_redirects=True) as client:
        for dest in dest_list:
            endpoints = [
                f"https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest={dest}&spp=30&nm={nm_id}",
                f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest={dest}&nm={nm_id}"
            ]

            for api_url in endpoints:
                try:
                    resp = await client.get(api_url)
                    if resp.status_code == 200:
                        data = resp.json()
                        products = data.get("data", {}).get("products", [])
                        if products:
                            prod = products[0]
                            title = prod.get("name") or title
                            price = _extract_price_from_product(prod)

                            if title and price is not None:
                                logger.info(f"✅ Успех! Найдено по dest={dest}")
                                break
                        else:
                            logger.info(f"⚠️ Пустой список товаров для dest={dest}")
                except Exception as e:
                    logger.warning(f"❌ Ошибка запроса {api_url}: {e}")

            if title and price is not None:
                break

        if not title:
            try:
                cdn_resp = await client.get(info_cdn_url)
                if cdn_resp.status_code == 200:
                    title = cdn_resp.json().get("imt_name") or cdn_resp.json().get("name")
            except Exception as e:
                logger.warning(f"❌ Ошибка CDN: {e}")

        if not title:
            title = f"Товар WB (Арт. {nm_id})"

        return {
            "nm_id": nm_id,
            "title": title,
            "price": price,
            "image_url": image_url,
        }