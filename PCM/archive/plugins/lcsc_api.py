"""Unofficial LCSC API."""

import io
from pathlib import Path
from typing import Union

import requests  # pylint: disable=import-error


class LCSC_API:
    """Unofficial LCSC API."""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        }  # pretend we are browser, otherwise their cloud service blocks the request
        self.szlcsc_headers = {
            "User-Agent": self.headers["User-Agent"],
            "Content-Type": "application/json",
            "Origin": "https://so.szlcsc.com",
            "Referer": "https://so.szlcsc.com/global.html",
        }

    def get_part_data(self, lcsc_number: str) -> dict:
        """Get data for a given LCSC number from the API."""
        r = requests.get(
            f"https://cart.jlcpcb.com/shoppingCart/smtGood/getComponentDetail?componentCode={lcsc_number}",
            headers=self.headers,
            timeout=10,
        )
        if r.status_code != requests.codes.ok:  # pylint: disable=no-member
            return {"success": False, "msg": "non-OK HTTP response status"}
        data = r.json()
        if not data.get("data"):
            return {
                "success": False,
                "msg": "returned JSON data does not have expected 'data' attribute",
            }
        return {"success": True, "data": data}

    def get_part_data_szlcsc(self, lcsc_number: str) -> dict:
        """Get component detail from SZLCSC using the search API."""
        payload = {
            "currentPage": 1,
            "pageSize": 10,
            "keyword": lcsc_number,
            "sortNumber": 0,
            "spotFilter": 1,
            "discountFilter": 1,
            "hasDataFile": False,
        }
        try:
            r = requests.post(
                "https://so.szlcsc.com/query/product",
                json=payload,
                headers=self.szlcsc_headers,
                timeout=15,
            )
        except requests.exceptions.RequestException as e:
            return {"success": False, "msg": f"Request failed: {e}"}

        if r.status_code != requests.codes.ok:
            return {"success": False, "msg": f"non-OK HTTP response: {r.status_code}"}

        try:
            raw = r.json()
        except ValueError:
            return {"success": False, "msg": "Invalid JSON response"}

        if raw.get("code") != 200:
            return {"success": False, "msg": f"API error {raw.get('code')}: {raw.get('msg')}"}

        search_result = (raw.get("result") or {}).get("searchResult") or {}
        items = search_result.get("productRecordList") or []
        if not items:
            return {"success": False, "msg": "No exact match found"}

        return {"success": True, "data": items[0]}


    def download_bitmap(self, url: str) -> Union[io.BytesIO, None]:
        """Download a picture of the part from the API."""
        headers = self.headers.copy()
        if "szlcsc" in url:
            headers["Referer"] = "https://item.szlcsc.com/"
        content = requests.get(url, headers=headers, timeout=10).content
        return io.BytesIO(content)

    def download_datasheet(self, url: str, path: Path):
        """Download and save a datasheet from the API."""
        r = requests.get(url, stream=True, headers=self.headers, timeout=10)
        if r.status_code != requests.codes.ok:  # pylint: disable=no-member
            return {"success": False, "msg": "non-OK HTTP response status"}
        if not r:
            return {"success": False, "msg": "Failed to download datasheet!"}
        with open(path, "wb") as f:
            f.write(r.content)
        return {"success": True, "msg": "Successfully downloaded datasheet!"}

    def search_szlcsc(self, keyword: str, page: int = 1, page_size: int = 30) -> dict:
        """Search SZLCSC for components by keyword."""
        payload = {
            "currentPage": page,
            "pageSize": page_size,
            "keyword": keyword,
            "sortNumber": 0,
            "spotFilter": 1,
            "discountFilter": 1,
            "hasDataFile": False,
        }
        try:
            r = requests.post(
                "https://so.szlcsc.com/query/product",
                json=payload,
                headers=self.szlcsc_headers,
                timeout=15,
            )
        except requests.exceptions.RequestException as e:
            return {"success": False, "msg": f"Request failed: {e}"}

        if r.status_code != requests.codes.ok:
            return {"success": False, "msg": f"non-OK HTTP response: {r.status_code}"}

        try:
            raw = r.json()
        except ValueError:
            return {"success": False, "msg": "Invalid JSON response"}

        if raw.get("code") != 200:
            return {"success": False, "msg": f"API error {raw.get('code')}: {raw.get('msg')}"}

        search_result = (raw.get("result") or {}).get("searchResult") or {}
        total = search_result.get("totalCount", 0)
        items = search_result.get("productRecordList") or []

        results = []
        _SMT_LABEL_MAP = {
            "SMT基础库": "Basic",
            "SMT扩展库": "Extended",
        }

        for item in items:
            vo = item.get("productVO") or {}
            prices = vo.get("productPriceList") or []
            unit_price = prices[0]["productPrice"] if prices else None
            product_id = vo.get("productId", "")
            url = f"https://item.szlcsc.com/{product_id}.html" if product_id else ""
            smt_label = vo.get("smtLabel", "")

            # The API also provides datasheet, though it isn't completely obvious
            # We'll use getComponentDetail to get datasheet lazily, but also try to get it if present
            datasheet = vo.get("pdfUrl", "") or ""

            results.append({
                "lcsc": vo.get("productCode", ""),
                "mfr_no": vo.get("productModel", ""),
                "package": vo.get("encapsulationModel", ""),
                "stock": vo.get("stockNumber", 0),
                "type": _SMT_LABEL_MAP.get(smt_label, ""),
                "mfr": vo.get("productGradePlateName", ""),
                "category": vo.get("productType", ""),
                "description": vo.get("productName", ""),
                "price": unit_price,
                "url": url,
                "datasheet": datasheet,
                "joints": 0,
            })

        return {"success": True, "total": total, "results": results}
