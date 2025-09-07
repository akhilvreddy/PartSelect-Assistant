# backend/scripts/build_installation_json.py
from playwright.sync_api import sync_playwright
import json, pathlib, re, time

BASE_URL = "https://www.partselect.com"
CATEGORY_PATHS = {
    "dishwasher": "/Dishwasher-Parts.htm",
    "refrigerator": "/Refrigerator-Parts.htm",
}
OUT_PATH = pathlib.Path("data/installation.json")
PS_RE = re.compile(r"\bPS\d{4,}\b", re.I)

def clean(s: str | None) -> str:
    return " ".join((s or "").split())

def get_part_type_links(page, category_url: str) -> list[str]:
    page.goto(category_url, timeout=60_000)
    page.wait_for_selector("#ShopByPartType", timeout=20_000)
    links = page.locator("#ShopByPartType + ul a")
    out = []
    for i in range(links.count()):
        href = links.nth(i).get_attribute("href")
        if href:
            out.append(BASE_URL + href if href.startswith("/") else href)
    return out

def extract_part_links(page, part_type_url: str, limit: int | None) -> list[str]:
    page.goto(part_type_url, timeout=60_000)
    page.wait_for_timeout(1500)
    cards = page.locator("a.nf__part__detail__title")
    n = cards.count()
    if limit is not None:
        n = min(n, limit)
    out = []
    for i in range(n):
        href = cards.nth(i).get_attribute("href")
        if href and "/PS" in href:
            out.append(BASE_URL + href if href.startswith("/") else href)
    return out

def extract_install_block(page) -> str:
    # 1) explicit block near “Installation Instructions”
    markers = page.locator("text=Installation Instructions")
    if markers.count() > 0:
        container = markers.first.locator("xpath=ancestor::*[self::div or self::section][1]")
        paras = container.locator("p")
        if paras.count() > 0:
            return clean(" ".join(paras.nth(i).text_content() for i in range(min(4, paras.count()))))
    # 2) fallback: product description
    desc = page.locator("div[itemprop='description'], #productDescription, div.description, .pd__desc")
    if desc.count() > 0:
        return clean(desc.first.text_content())
    # 3) last resort: first paragraph on page
    anyp = page.locator("p")
    return clean(anyp.first.text_content()) if anyp.count() > 0 else ""

def extract_meta(page):
    diff, t_req = "", ""
    meta = page.locator("div.d-flex.flex-lg-grow-1.col-lg-7.col-12.justify-content-lg-between.mt-lg-0.mt-2 .d-flex p")
    if meta.count() >= 2:
        diff = clean(meta.nth(0).text_content())
        t_req = clean(meta.nth(1).text_content())
    return diff, t_req

def scrape_part(page, url: str) -> dict | None:
    page.goto(url, timeout=60_000)
    page.wait_for_selector("h1", timeout=20_000)
    title = clean(page.locator("h1").first.text_content())
    body  = page.locator("body").text_content()
    m = PS_RE.search(body) or PS_RE.search(url)
    ps = m.group(0) if m else ""

    text = extract_install_block(page)
    diff, t_req = extract_meta(page)

    if not title or not text:
        return None

    return {
        "id": f"{(ps or title)[:40]}-install",
        "part_number": ps,
        "title": title,
        "url": url,
        "difficulty": diff if diff and diff != "N/A" else "",
        "time_required": t_req if t_req and t_req != "N/A" else "",
        "tools": [],
        "text": text or "See product page for detailed steps."
    }

def main(appliance: str = "dishwasher", per_type_limit: int = 3, headless: bool = False):
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    docs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        # gather all part-type links for both dishwasher + refrigerator
        for appliance_key in ["dishwasher", "refrigerator"]:
            category_url = BASE_URL + CATEGORY_PATHS[appliance_key]
            ctx = browser.new_context()
            page = ctx.new_page()
            part_type_links = get_part_type_links(page, category_url)
            ctx.close()

            for pt in part_type_links:
                ctx2 = browser.new_context()
                page2 = ctx2.new_page()
                part_links = extract_part_links(page2, pt, per_type_limit)
                ctx2.close()

                # scrape each part
                ctx3 = browser.new_context()
                page3 = ctx3.new_page()
                for link in part_links:
                    try:
                        d = scrape_part(page3, link)
                        if d:
                            docs.append(d)
                    except Exception as e:
                        print("skip:", e)
                    page3.wait_for_timeout(350)
                ctx3.close()
                time.sleep(0.2)

        browser.close()

    OUT_PATH.write_text(json.dumps(docs, indent=2))
    print(f"Wrote {OUT_PATH} with {len(docs)} docs")

if __name__ == "__main__":
    main()