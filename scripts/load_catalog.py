#!/usr/bin/env python3
import json
import requests
from pathlib import Path

ES_URL = "http://localhost:9200"
INDEX = "products"
JSON_FILE = Path("data/catalog.json")


def load_catalog():
    # Загружаем JSON
    with JSON_FILE.open(encoding="utf-8") as f:
        items = json.load(f)

    bulk_lines = []

    for obj in items:
        # Header
        bulk_lines.append(json.dumps({"index": {"_index": INDEX, "_id": obj["id"]}}))
        
        # Ensure numeric fields are correct types
        if "weight" in obj:
            try:
                obj["weight"] = float(obj["weight"])
            except Exception:
                pass
        if "package_size" in obj:
            try:
                obj["package_size"] = int(obj["package_size"])
            except Exception:
                pass
        if "price" in obj:
            try:
                obj["price"] = float(obj["price"])
            except Exception:
                pass

        # Document
        bulk_lines.append(json.dumps(obj, ensure_ascii=False))

    # Bulk body
    body = "\n".join(bulk_lines) + "\n"

    # Отправка запроса
    r = requests.post(
        f"{ES_URL}/_bulk",
        data=body,
        headers={"Content-Type": "application/x-ndjson"}
    )

    print(r.status_code)
    print(r.text)


if __name__ == "__main__":
    load_catalog()

