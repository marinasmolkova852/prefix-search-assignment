from fastapi import FastAPI, Query
from typing import List
from opensearchpy import OpenSearch
from reranker import rerank_smart

app = FastAPI()

# Инициализация OpenSearch
client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_compress=True,
)

INDEX = "products"

@app.get("/search")
def search(q: str = Query(..., min_length=1), site: str = None, top_k: int = 5):
    """
    Поиск с префиксами + reranker
    """
    # 1. Запрос к OpenSearch
    os_query = {
        "size": top_k * 2,  # берём больше для последующего rerank
        "query": {
            "multi_match": {
                "query": q,
                "type": "bool_prefix",
                "fields": [
                    "name^3",
                    "keywords^2",
                    "category^2",
                    "brand^2"
                ]
            }
        }
    }

    res = client.search(index=INDEX, body=os_query)
    hits = [hit["_source"] for hit in res["hits"]["hits"]]

    # 2. Применяем умный reranker
    ranked = rerank_smart(q, hits, expected_category=site)

    # 3. Возвращаем top_k результатов
    return {"results": ranked[:top_k]}

