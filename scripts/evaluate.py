import csv, requests

API = "http://localhost:8000/search"

def evaluate():
    rows = csv.DictReader(open("data/prefix_queries.csv"))
    ok = 0
    total = 0

    for r in rows:
        q = r["query"]
        cat = r["expected_category"]

        resp = requests.get(API, params={"q": q}).json()
        top = resp["results"][:3]

        if any(h["_source"]["category"] == cat for h in top):
            ok += 1
        total += 1

    print("Precision@3:", ok / total)

if __name__ == "__main__":
    evaluate()
