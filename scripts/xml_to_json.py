import xml.etree.ElementTree as ET
import json
from pathlib import Path

def parse_weight(elem):
    """Парсинг <weight unit="g">900</weight> + нормализация."""
    if elem is None or elem.text is None:
        return None, None
    
    value = elem.text.strip()
    try:
        value = float(value.replace(",", "."))
    except:
        value = None
    
    unit = elem.attrib.get("unit")  # g, ml, kg, L, pcs …
    return value, unit


def parse_price(elem):
    """Парсинг цены <price currency="RUB">151.23</price>."""
    if elem is None or elem.text is None:
        return None, None
    
    value = float(elem.text.replace(",", "."))
    currency = elem.attrib.get("currency", "RUB")
    return value, currency


def convert_xml_to_json(file_in="data/catalog_products.xml",
                        file_out="data/catalog.json"):
    tree = ET.parse(file_in)
    root = tree.getroot()

    products = []

    for p in root.findall("product"):
        pid = p.attrib.get("id")  # ID теперь атрибут!

        name = p.findtext("name", default="")
        brand = p.findtext("brand", default="")
        category = p.findtext("category", default="")
        keywords = p.findtext("keywords", default="")
        description = p.findtext("description", default="")
        image = p.findtext("image_url", default="")

        # weight parsing
        weight_value, weight_unit = parse_weight(p.find("weight"))

        # price parsing
        price_value, price_currency = parse_price(p.find("price"))

        # package_size
        try:
            package_size = float(p.findtext("package_size", default="1"))
        except:
            package_size = 1

        products.append({
            "id": pid,
            "name": name,
            "brand": brand,
            "category": category,
            "keywords": keywords,
            "description": description,
            "image_url": image,

            # normalized values
            "weight": weight_value,
            "weight_unit": weight_unit,
            "package_size": package_size,

            "price": price_value,
            "price_currency": price_currency
        })

    Path(file_out).write_text(json.dumps(products, indent=2, ensure_ascii=False))
    print(f"Saved {len(products)} products to {file_out}")


if __name__ == "__main__":
    convert_xml_to_json()

