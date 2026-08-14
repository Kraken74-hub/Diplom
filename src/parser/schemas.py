from pydantic import BaseModel

class WBProduct(BaseModel):
    """Схема валидации одного товара из ответа WB API"""
    id: int
    name: str
    salePriceU: int  # Цена возвращается в копейках

class WBData(BaseModel):
    """Схема блока 'data' ответа WB API"""
    products: list[WBProduct]

class WBResponse(BaseModel):
    """Корневая схема JSON-ответа от API card.wb.ru"""
    data: WBData