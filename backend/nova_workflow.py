from __future__ import annotations

import json
from typing import List

from .config import get_settings
from .models import SearchMode, SupplierResult, SearchResponse

try:
    # The real SDK, installed via `pip install nova-act`
    from nova_act import NovaAct
except ImportError:  # pragma: no cover - allows type checking without SDK
    NovaAct = None  # type: ignore[misc,assignment]


SUPPLIER_SITES_BY_MODE: dict[SearchMode, List[str]] = {
    "broad_web": [
        "https://www.google.com/search?q=suppliers",
        "https://www.bing.com/search?q=suppliers",
    ],
    "marketplace": [
        "https://www.alibaba.com/",
        "https://www.amazon.com/",
    ],
    "b2b": [
        "https://www.thomasnet.com/",
        "https://www.globalsources.com/",
    ],
}


def _ensure_sdk():
    if NovaAct is None:
        raise RuntimeError(
            "nova-act SDK is not installed. Install with `pip install nova-act` in the backend environment."
        )


async def run_supplier_search(query: str, mode: SearchMode) -> SearchResponse:
    """
    Use Nova Act to search for suppliers across multiple sites with basic failover.

    We instruct Nova Act to return strict JSON so the backend can parse it reliably.
    """
    _ensure_sdk()
    settings = get_settings()
    sites = SUPPLIER_SITES_BY_MODE.get(mode, SUPPLIER_SITES_BY_MODE["broad_web"])

    all_suppliers: list[SupplierResult] = []
    used_sites: list[str] = []

    # Simple sequential failover across sites
    for site in sites:
        used_sites.append(site)
        try:
            with NovaAct(
                starting_page=site,
                api_key=settings.nova_act_api_key,
                model_id=settings.nova_act_model_id,
            ) as nova:
                prompt = (
                    "You are an automated procurement assistant.\n"
                    f"Search this site for suppliers for the product: '{query}'.\n"
                    "Return a JSON array named `suppliers`, where each item has:\n"
                    "  - name (string, supplier or product name)\n"
                    "  - url (string, absolute URL to the supplier or product page)\n"
                    "  - snippet (string, short summary or description if visible)\n"
                    "  - source (string, like 'google', 'alibaba', 'b2b directory')\n"
                    "If no suppliers are found on this site, return `suppliers: []`.\n"
                    "Output ONLY valid JSON, no backticks, no extra text."
                )
                result_text = nova.act(prompt)  # type: ignore[operator]

            data = json.loads(result_text)
            suppliers_raw = data.get("suppliers") or []
            for item in suppliers_raw:
                try:
                    supplier = SupplierResult(
                        name=item.get("name") or "Unknown supplier",
                        url=item.get("url"),
                        snippet=item.get("snippet"),
                        source=item.get("source") or site,
                        estimated_price=item.get("estimated_price"),
                    )
                    all_suppliers.append(supplier)
                except Exception:
                    # Ignore malformed entries; keep going
                    continue

            # If we successfully got any suppliers from this site, we can stop early
            if all_suppliers:
                break
        except Exception:
            # If anything goes wrong for this site, move on to the next
            continue

    return SearchResponse(
        query=query,
        mode=mode,
        suppliers=all_suppliers,
        used_sites=used_sites,
    )

