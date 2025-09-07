# backend/scripts/scrape_parts.py
import csv
import time
import argparse
from pathlib import Path
from typing import List, Dict

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

BASE_URL = "https://www.partselect.com"

CATEGORY_PATHS = {
    "dishwasher": "/Dishwasher-Parts.htm",
    "refrigerator": "/Refrigerator-Parts.htm",
}

def get_part_type_links(page, category_url: str) -> List[str]:
    """Collect links for each part-type within the category page."""
    page.goto(category_url, timeout=60_000)
    page.wait_for_selector("#ShopByPartType", timeout=20_000)
    part_type_links = []
    links = page.locator("#ShopByPartType + ul a")
    for i in range(links.count()):
        href = links.nth(i).get_attribute("href")
        if href:
            full = BASE_URL + href if href.startswith("/") else href
            part_type_links.append(full)
    return part_type_links

def extract_all_part_links(page, part_type_url: str, limit: int | None) -> List[str]:
    """From a part-type page, collect links to individual part detail pages."""
    page.goto(part_type_url, timeout=60_000)
    page.wait_for_timeout(1_500)
    links = []
    cards = page.locator("a.nf__part__detail__title")
    count = cards.count()
    if limit is not None:
        count = min(count, int(limit))
    for i in range(count):
        href = cards.nth(i).get_attribute("href")
        if href and "/PS" in href:
            full = BASE_URL + href if href.startswith("/") else href
            links.append(full)
    return links

def extract_part_data(page, url: str) -> Dict[str, str]:
    """Visit a part page and extract structured fields."""
    page.goto(url, timeout=60_000)
    page.wait_for_selector("h1", timeout=20_000)

    def safe_get(selector: str) -> str:
        try:
            loc = page.locator(selector)
            if loc.count() > 0:
                return loc.first.text_content().strip()
            return "N/A"
        except Exception:
            return "N/A"

    def get_video_url() -> str:
        try:
            yt_div = page.locator("div.yt-video")
            if yt_div.count() > 0:
                yt_id = yt_div.first.get_attribute("data-yt-init")
                if yt_id:
                    return f"https://www.youtube.com/watch?v={yt_id}"
            return "N/A"
        except Exception:
            return "N/A"

    def get_text_after(header_text: str) -> str:
        blocks = page.locator("div.col-md-6.mt-3")
        for i in range(blocks.count()):
            text = blocks.nth(i).text_content()
            if header_text.lower() in (text or "").lower():
                stripped = text.split(":", 1)[-1].strip()
                return ", ".join([t.strip() for t in stripped.split(",")])
        return "N/A"

    def get_install_info() -> tuple[str, str]:
        difficulty = "N/A"
        time_required = "N/A"
        info_block = page.locator("div.d-flex.flex-lg-grow-1.col-lg-7.col-12.justify-content-lg-between.mt-lg-0.mt-2")
        if info_block.count() > 0:
            items = info_block.first.locator(".d-flex p")
            if items.count() >= 2:
                difficulty = items.nth(0).text_content().strip()
                time_required = items.nth(1).text_content().strip()
        return difficulty, time_required

    def get_related_parts() -> str:
        try:
            wrap = page.locator("div.pd__related-part-wrap")
            if wrap.count() > 0:
                parts = []
                part_divs = wrap.locator("div.pd__related-part")
                for i in range(part_divs.count()):
                    a_tag = part_divs.nth(i).locator("a").first
                    name = a_tag.text_content().strip()
                    link = a_tag.get_attribute("href")
                    full = BASE_URL + link if link and link.startswith("/") else link
                    parts.append(f"{name} ({full})")
                return " | ".join(parts) if parts else "N/A"
            return "N/A"
        except Exception:
            return "N/A"

    def get_replacement_parts() -> str:
        try:
            blocks = page.locator("div.col-md-6.mt-3")
            for i in range(blocks.count()):
                text = blocks.nth(i).text_content()
                if text and "replaces these:" in text.lower():
                    return text.split("replaces these:", 1)[-1].strip()
            return "N/A"
        except Exception:
            return "N/A"

    def get_description() -> str:
        try:
            desc = page.locator("div[itemprop='description']")
            if desc.count() > 0:
                return desc.first.text_content().strip()
            return "N/A"
        except Exception:
            return "N/A"

    difficulty, install_time = get_install_info()

    return {
        "url": url,
        "title": safe_get("h1"),
        "part_id": safe_get("span[itemprop='productID']"),
        "brand": safe_get("span[itemprop='brand'] span[itemprop='name']"),
        "availability": safe_get("span[itemprop='availability']"),
        "price": safe_get("span.price.pd__price span.js-partPrice"),
        "symptoms": get_text_after("symptoms"),
        "product_types": get_text_after("products"),
        "installation_difficulty": difficulty,
        "installation_time": install_time,
        "related_parts": get_related_parts(),
        "replacement_parts": get_replacement_parts(),
        "video_url": get_video_url(),
        "description": get_description(),
    }

def save_streamed_row(row: Dict[str, str], file_path: Path):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = file_path.exists()
    with file_path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def scrape_part_type_page(browser, part_type_url: str, out_csv: Path, limit: int | None):
    context = browser.new_context()
    page = context.new_page()
    try:
        part_links = extract_all_part_links(page, part_type_url, limit)
        print(f"  • Found {len(part_links)} part links in: {part_type_url}")
        for i, link in enumerate(part_links, start=1):
            print(f"    [{i}/{len(part_links)}] {link}")
            try:
                data = extract_part_data(page, link)
                save_streamed_row(data, out_csv)
            except PWTimeout:
                print("      (timeout) skipping this part")
            except Exception as e:
                print(f"      (error) {e}")
            page.wait_for_timeout(400)
    finally:
        context.close()

def run(appliance: str, limit: int | None, headless: bool, out_dir: Path):
    if appliance not in CATEGORY_PATHS:
        raise ValueError(f"appliance must be one of {list(CATEGORY_PATHS)}")

    category_url = BASE_URL + CATEGORY_PATHS[appliance]
    out_csv = out_dir / f"appliance_parts_{appliance}.csv"

    print(f"→ Scraping {appliance} parts")
    print(f"  Category: {category_url}")
    print(f"  Output:   {out_csv}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        # First page: collect part-type links
        context = browser.new_context()
        page = context.new_page()
        print("Collecting part-type links…")
        part_type_links = get_part_type_links(page, category_url)
        print(f"Found {len(part_type_links)} part types")
        context.close()

        # For each part-type, scrape a (limited) set of parts
        for idx, link in enumerate(part_type_links, start=1):
            print(f"\nPart type {idx}/{len(part_type_links)}: {link}")
            scrape_part_type_page(browser, link, out_csv, limit)
            time.sleep(0.3)

        browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape PartSelect parts data to CSV.")
    parser.add_argument("--appliance", choices=["dishwasher", "refrigerator"], required=True)
    parser.add_argument("--limit", type=int, default=20, help="Max parts per part-type page (default: 20)")
    parser.add_argument("--headless", action="store_true", help="Run browser headlessly")
    parser.add_argument(
        "--outdir",
        type=str,
        default="/Users/akhilvreddy/Documents/PartSelect-Assistant/backend/data",
        help="Output directory for CSV"
    )
    args = parser.parse_args()

    run(
        appliance=args.appliance,
        limit=args.limit,
        headless=args.headless,
        out_dir=Path(args.outdir)
    )