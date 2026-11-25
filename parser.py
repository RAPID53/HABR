import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

proto = "https" + ":" + "//"
host = ".".join(["habr", "com"])
RSS_URL = proto + host + "/ru/rss/all/all/"
OUTPUT_FILE = Path("habr_articles.txt")

def get_existing_lines_and_urls(file_path: Path):
    if not file_path.exists():
        return [], set()
    lines = []
    urls = set()
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            clean_line = line.strip()
            if not clean_line:
                continue
            lines.append(clean_line)
            parts = clean_line.split(" | ")
            if len(parts) >= 3:
                urls.add(parts.pop().strip())
    return lines, urls

def main():
    old_lines, seen_urls = get_existing_lines_and_urls(OUTPUT_FILE)
    
    req = urllib.request.Request(
        RSS_URL,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        xml_data = resp.read()

    root = ET.fromstring(xml_data)
    new_lines = []

    for item in root.findall("./channel/item"):
        link_el = item.find("link")
        title_el = item.find("title")
        pub_el = item.find("pubDate")

        if link_el is None or not link_el.text:
            continue

        clean_url = link_el.text.split("?").pop(0).strip()
        if clean_url in seen_urls:
            continue

        title = title_el.text.strip().replace("\n", " ").replace("|", "-") if title_el is not None and title_el.text else "Без назви"
        
        if pub_el is not None and pub_el.text:
            try:
                dt = parsedate_to_datetime(pub_el.text.strip())
                pub_date = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                pub_date = pub_el.text.strip()
        else:
            pub_date = "Невідома дата"

        new_lines.append(f"{pub_date} | {title} | {clean_url}")
        seen_urls.add(clean_url)

    if new_lines:
        all_lines = new_lines + old_lines
        with OUTPUT_FILE.open("w", encoding="utf-8") as f:
            f.write("\n".join(all_lines) + "\n")
        print(f"Додано нових статей: {len(new_lines)}")
    else:
        print("Нових статей немає.")

if __name__ == "__main__":
    main()
