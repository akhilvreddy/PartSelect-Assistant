# backend/scripts/build_troubleshooting_json.py
"""
Creates data/troubleshooting.json

One document per PART (#PS…), each with the list of symptoms this
part fixes (as shown in the “Troubleshooting” tab on the part page).

{ "id": "tr-PS11757388",
  "appliance": "dishwasher",
  "part_number": "PS11757388",
  "title": "Dishwasher Circulation Pump And Motor WPW10757217",
  "url": "https://www.partselect.com/PS11757388-Whirlpool-....htm",
  "symptoms": [
      { "symptom": "Not draining",  "fix_percentage": 45,
        "description": "If the dishwasher will not drain ..." },
      ...
  ],
  "text": "This part is linked to 4 common symptoms, e.g. Not draining (45 %)."
}
"""

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import pathlib, json, re, time, hashlib, sys

# ---------- configuration ---------------------------------------------------
BASE = "https://www.partselect.com"
CATEGORY = {
    "dishwasher":   "/Dishwasher-Parts.htm",
    "refrigerator": "/Refrigerator-Parts.htm",
}
OUT_PATH       = pathlib.Path("data/troubleshooting.json")
PER_TYPE_LIMIT = 8          # parts per part-type page  (raise for bigger corpus)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/118.0.0.0 Safari/537.36")

# ---------- helpers ---------------------------------------------------------
CLEAN = lambda s: " ".join((s or "").split())
PS_RE = re.compile(r"\bPS\d{4,}\b", re.I)
SYMPTAB_RE = re.compile(r"(\d{1,3})%")

def digest(appliance: str, part: str) -> str:
    return hashlib.md5(f"{appliance}:{part}".encode()).hexdigest()[:12]

def get_part_type_links(page, category_url):
    page.goto(category_url, timeout=60_000)
    page.wait_for_selector("#ShopByPartType", timeout=20_000)
    links = []
    for i in range(page.locator("#ShopByPartType + ul a").count()):
        href = page.locator("#ShopByPartType + ul a").nth(i).get_attribute("href")
        if href:
            links.append(BASE + href if href.startswith("/") else href)
    return links

def get_part_links(page, part_type_url, limit):
    page.goto(part_type_url, timeout=60_000)
    page.wait_for_timeout(1500)
    cards = page.locator("a.nf__part__detail__title")
    out   = []
    for i in range(min(cards.count(), limit)):
        href = cards.nth(i).get_attribute("href")
        if href and "/PS" in href:
            out.append(BASE + href if href.startswith("/") else href)
    return out

def extract_troubleshooting(page):
    # click the Troubleshooting tab if present
    try:
        tab = page.locator("text=Troubleshooting").first
        if tab.count():
            tab.click(); page.wait_for_timeout(400)
    except Exception:
        pass

    rows = page.locator("div[id^='troubleshooting'] div.symptoms")
    data = []
    for i in range(rows.count()):
        row = rows.nth(i)
        try:
            symp = CLEAN(row.locator("div.symptoms__header").text_content())
            pct_raw = row.locator("div.symptoms__percent span.bold").text_content()
            pct = int(SYMPTAB_RE.search(pct_raw).group(1)) if pct_raw else None
            desc = CLEAN(row.locator("p.mb-4").text_content())
            data.append({"symptom": symp,
                         "fix_percentage": pct,
                         "description": desc})
        except Exception:
            continue
    return data

def scrape_part(page, url, appliance):
    try:
        page.goto(url, timeout=60_000)
        page.wait_for_selector("h1", timeout=20_000)
    except PWTimeout:
        return None

    title = CLEAN(page.locator("h1").first.text_content())
    m     = PS_RE.search(url) or PS_RE.search(title)
    part  = m.group(0) if m else title[:30]

    symps = extract_troubleshooting(page)
    if not symps:
        return None

    return {
        "id": f"tr-{digest(appliance, part)}",
        "appliance": appliance,
        "part_number": part,
        "title": title,
        "url": url.split("?",1)[0],
        "symptoms": symps,
        "text": (f"This part is linked to {len(symps)} common symptoms, "
                 f"e.g. {symps[0]['symptom']} ({symps[0]['fix_percentage']} %).")
    }

# ---------- main ------------------------------------------------------------
def main(headless=True):
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    docs, seen = [], set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        ctx     = browser.new_context(user_agent=UA)
        page    = ctx.new_page()

        for appliance, cat in CATEGORY.items():
            print(f"⇢ {appliance}")
            part_type_links = get_part_type_links(page, BASE + cat)

            for pt_link in part_type_links:
                part_links = get_part_links(page, pt_link, PER_TYPE_LIMIT)
                for link in part_links:
                    doc = scrape_part(page, link, appliance)
                    if doc and doc["id"] not in seen:
                        docs.append(doc); seen.add(doc["id"])
                        print("  •", doc["part_number"], "->", doc["symptoms"][0]["symptom"])
                    time.sleep(0.2)

        browser.close()

    OUT_PATH.write_text(json.dumps(docs, indent=2))
    print("\nWrote", len(docs), "docs →", OUT_PATH.resolve())

if __name__ == "__main__":
    # run visible once; flip headless=True when happy
    main(headless=False if "--show" in sys.argv else True)