from typing import List, Literal, Optional

from pydantic import BaseModel, HttpUrl


SearchMode = Literal["broad_web", "marketplace", "b2b"]


class SearchRequest(BaseModel):
    query: str
    mode: SearchMode = "broad_web"


class SupplierAction(str):
    BUY = "buy_now"
    INQUIRE = "inquire"
    CONNECT_SHOPIFY = "connect_shopify"


class SupplierResult(BaseModel):
    name: str
    url: HttpUrl
    snippet: Optional[str] = None
    source: Optional[str] = None
    estimated_price: Optional[str] = None
    actions: List[str] = [SupplierAction.BUY, SupplierAction.INQUIRE, SupplierAction.CONNECT_SHOPIFY]


class SearchResponse(BaseModel):
    query: str
    mode: SearchMode
    suppliers: List[SupplierResult]
    used_sites: List[str]


class HistoryItem(BaseModel):
    id: str
    query: str
    mode: SearchMode


class HistoryResponse(BaseModel):
    items: List[HistoryItem]


class DemoActionRequest(BaseModel):
    supplier_url: HttpUrl
    supplier_name: str


class DemoActionResponse(BaseModel):
    status: Literal["ok"]
    message: str
    details: dict

