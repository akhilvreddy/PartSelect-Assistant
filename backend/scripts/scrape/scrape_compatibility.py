# backend/scripts/build_compatibility_json.py
from playwright.sync_api import sync_playwright
import json, pathlib, re, time

BASE_URL = "https://www.partselect.com"
CATEGORY_PATHS = {
    "dishwasher": "/Dishwasher-Parts.htm",
    "refrigerator": "/Refrigerator-Parts.htm",
}
OUT_PATH = pathlib.Path("data/compatibility.json")

PS_RE     = re.compile(r"\bPS\d{4,}\b", re.I)
MODEL_RE  = re.compile(r"\b[A-Z0-9-]{5,}\b")

BRAND_HINTS = [
    "Whirlpool", "KitchenAid", "Maytag", "GE", "Frigidaire",
    "Samsung", "LG", "Bosch", "Amana", "Kenmore"
]

def clean(s: str | None) -> str:
    return " ".join((s or "").split())

# ---------- shared helpers (same as your install script) ----------
def get_part_type_links(page, category_url: str) -> list[str]:
    page.goto(category_url, timeout=60_000)
    page.wait_for_selector("#ShopByPartType", timeout=20_000)
    links = page.locator("#ShopByPartType + ul a")
    return [
        BASE_URL + href if href.startswith("/") else href
        for i in range(links.count())
        if (href := links.nth(i).get_attribute("href"))
    ]

def extract_part_links(page, part_type_url: str, limit: int | None) -> list[str]:
    page.goto(part_type_url, timeout=60_000)
    page.wait_for_timeout(1_500)
    cards = page.locator("a.nf__part__detail__title")
    n = cards.count() if limit is None else min(cards.count(), limit)
    return [
        BASE_URL + href if href.startswith("/") else href
        for i in range(n)
        if (href := cards.nth(i).get_attribute("href")) and "/PS" in href
    ]

# ---------- NEW: per-part compatibility extractor ----------
def extract_models_brands_text(page) -> tuple[list[str], list[str], str]:
    """
    Returns ([models], [brands], raw_text_with_models)
    """
    # 1) Try common 'works with' sections
    blocks = page.locator(
        "text=This part works with, text=Models this part fits, text=Fits models"
    )
    raw = ""
    if blocks.count() > 0:
        container = blocks.first.locator("xpath=ancestor::*[self::div or self::section][1]")
        raw = container.text_content() or ""
    # 2) Fallback: whole body (we'll still cap after extraction)
    if not raw:
        raw = page.locator("body").text_content() or ""

    models = [
        m for m in MODEL_RE.findall(raw) if not m.startswith("PS")
    ]
    models = list(dict.fromkeys(models))[:50]  # dedupe + cap

    brands = [
        b for b in BRAND_HINTS if b.lower() in raw.lower()
    ]

    return models, brands, clean(raw[:800])  # keep first 800 chars for text blob

def scrape_part_compat(page, url: str) -> dict | None:
    """Extract a single part page into a compatibility doc."""
    page.goto(url, timeout=60_000)
    page.wait_for_selector("h1", timeout=20_000)

    title = clean(page.locator("h1").first.text_content())
    body  = page.locator("body").text_content() or ""
    m = PS_RE.search(body) or PS_RE.search(url)
    ps = m.group(0) if m else ""

    models, brands, raw = extract_models_brands_text(page)
    if not title or not models:
        return None  # skip parts without model list

    return {
        "id": f"{(ps or title)[:40]}-compat",
        "part_number": ps,
        "title": title,
        "url": url.split("?", 1)[0],
        "models": models,
        "brands": brands,
        "notes": "",
        "text": f"Compatible models: {', '.join(models[:40])}. {raw}"
    }

# ---------- crawl driver ----------
def main(per_type_limit: int = 3, headless: bool = False):
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    docs, seen = [], set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)

        for appliance in ["dishwasher", "refrigerator"]:
            category_url = BASE_URL + CATEGORY_PATHS[appliance]
            ctx = browser.new_context()
            page = ctx.new_page()
            part_type_links = get_part_type_links(page, category_url)
            ctx.close()

            for pt in part_type_links:
                ctx2 = browser.new_context()
                page2 = ctx2.new_page()
                part_links = extract_part_links(page2, pt, per_type_limit)
                ctx2.close()

                ctx3 = browser.new_context()
                page3 = ctx3.new_page()
                for link in part_links:
                    try:
                        d = scrape_part_compat(page3, link)
                        if d and d["id"] not in seen:
                            seen.add(d["id"])
                            docs.append(d)
                    except Exception as e:
                        print("skip:", e)
                    page3.wait_for_timeout(350)
                ctx3.close()
                time.sleep(0.25)

        browser.close()

    OUT_PATH.write_text(json.dumps(docs, indent=2))
    print(f"Wrote {OUT_PATH} with {len(docs)} docs")

if __name__ == "__main__":
    # Grab ~3 parts per part-type page → ends up with ~100–150 docs, plenty.
    main(per_type_limit=3, headless=False)  # set headless=True once it works