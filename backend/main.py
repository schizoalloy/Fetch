from __future__ import annotations

import uuid
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    DemoActionRequest,
    DemoActionResponse,
    HistoryItem,
    HistoryResponse,
    SearchRequest,
    SearchResponse,
)
from .nova_workflow import run_supplier_search

app = FastAPI(title="Nova Act Supplier Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


_history: List[HistoryItem] = []


@app.post("/search", response_model=SearchResponse)
async def search_suppliers(body: SearchRequest) -> SearchResponse:
    res = await run_supplier_search(body.query, body.mode)

    _history.insert(
        0,
        HistoryItem(
            id=str(uuid.uuid4()),
            query=res.query,
            mode=res.mode,
        ),
    )
    # Keep only recent entries
    if len(_history) > 50:
        del _history[50:]

    return res


@app.get("/history", response_model=HistoryResponse)
async def get_history() -> HistoryResponse:
    return HistoryResponse(items=_history)


@app.post("/actions/buy", response_model=DemoActionResponse)
async def demo_buy_now(body: DemoActionRequest) -> DemoActionResponse:
    # Demo implementation: in a real app, you could instruct Nova Act
    # to navigate to the supplier_url and attempt a checkout flow.
    return DemoActionResponse(
        status="ok",
        message=f"Pretending to execute 'Buy Now' for {body.supplier_name}.",
        details={
            "supplier_url": str(body.supplier_url),
            "action": "buy_now",
        },
    )


@app.post("/actions/inquire", response_model=DemoActionResponse)
async def demo_inquire(body: DemoActionRequest) -> DemoActionResponse:
    return DemoActionResponse(
        status="ok",
        message=f"Pretending to send an inquiry to {body.supplier_name}.",
        details={
            "supplier_url": str(body.supplier_url),
            "action": "inquire",
        },
    )


@app.post("/actions/connect-shopify", response_model=DemoActionResponse)
async def demo_connect_shopify(body: DemoActionRequest) -> DemoActionResponse:
    return DemoActionResponse(
        status="ok",
        message=f"Pretending to connect {body.supplier_name} to Shopify.",
        details={
            "supplier_url": str(body.supplier_url),
            "action": "connect_shopify",
        },
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

