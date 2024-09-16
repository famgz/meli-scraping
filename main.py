import requests
import json
from bs4 import BeautifulSoup
from pathlib import Path

source_dir = Path(__file__).parent.resolve()
data_dir = Path(source_dir, "data")
data_dir.mkdir(exist_ok=True)

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.5",
    "priority": "u=0, i",
    "referer": "https://lista.mercadolivre.com.br",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Brave";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "sec-gpc": "1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
}


def get_web_html(url):
    return requests.get(
        url,
        cookies=None,
        headers=headers,
    ).content


def get_local_html():
    path = Path(source_dir, "sample.html")
    if not path.exists():
        print("Invalid path:", path)
        return
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def save_html(data):
    with open(Path(source_dir, "sample.html"), "wb") as f:
        f.write(data)


def main():

    url = "https://lista.mercadolivre.com.br/tenis-corrida-masculino"

    data = get_web_html(url)
    save_html(data)

    page = BeautifulSoup(data, "lxml")

    data = None
    script = page.select_one("script[data-head-react=true]")
    if not script:
        print("invalid data")
        exit(1)

    data = json.loads(script.text)

    initialState = data["pageState"]["initialState"]

    [available_filters] = [
        x["filters"]
        for x in initialState["sidebar"]["components"]
        if x["type"] == "AVAILABLE_FILTERS"
    ]

    [brands] = [x["values"] for x in available_filters if x["id"] == "BRAND"]

    unique_brands = {x["name"] for x in brands}

    products = initialState["results"]

    print(len(brands), "brands")
    print(len(unique_brands), "unique brands")
    print(len(products), "products")

    # save brands in JSON
    save_json(Path(data_dir, "brands.json"), brands)

    # save products in JSON
    save_json(Path(data_dir, "products.json"), products)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e)
