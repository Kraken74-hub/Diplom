from pydantic import BaseModel

class Price(BaseModel):
    """Схема цены товара (в копейках)"""
    basic: int | None = None
    product: int | None = None
    total: int | None = None

class Size(BaseModel):
    """Схема размера товара"""
    name: str | None = None
    origName: str | None = None
    price: Price | None = None

class WBProduct(BaseModel):
    """Схема одного товара из ответа WB API v2"""
    id: int
    name: str
    sizes: list[Size] = []
    salePriceU: int | None = None  # Фолбэк для совместимости

class WBData(BaseModel):
    """Схема контейнера data"""
    products: list[WBProduct] = []

class WBResponse(BaseModel):
    """Корневая схема ответа card.wb.ru"""
    data: WBData