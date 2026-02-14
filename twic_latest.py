#!/usr/bin/env python3
import os
import pathlib
import re
import urllib.request

BASE_URL = "https://theweekinchess.com"
TWIC_PAGE = f"{BASE_URL}/twic"
DOWNLOAD_DIR = str(pathlib.Path.home() / "Downloads")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
)


def fetch_page(url):
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def get_latest_pgn_url(html: str) -> str:
    """
    Find all twicNNNNg.zip links and return the one with the highest issue number.
    """
    zip_links = re.findall(r'href="([^"]*twic(\d+)g\.zip)"', html, re.IGNORECASE)
    if not zip_links:
        raise RuntimeError("No TWIC PGN zip links found")

    # Sort by issue number (descending) and take the first
    zip_links.sort(key=lambda x: int(x[1]), reverse=True)
    url = zip_links[0][0]

    # Make absolute if needed
    if url.startswith("http"):
        return url
    return BASE_URL + url


def download_file(url: str, dest_path: str):
    if os.path.exists(dest_path):
        print(f"File already exists: {dest_path}")
        return
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    headers = {"User-Agent": USER_AGENT}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp, open(dest_path, "wb") as f:
        f.write(resp.read())
    print(f"Downloaded: {dest_path}")


def unzip_file(zip_path: str):
    import zipfile

    extract_dir = os.path.dirname(zip_path)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"Extracted to: {extract_dir}")


def main():
    html = fetch_page(TWIC_PAGE)
    pgn_url = get_latest_pgn_url(html)
    filename = os.path.basename(pgn_url)
    dest = os.path.join(DOWNLOAD_DIR, filename)
    download_file(pgn_url, dest)
    unzip_file(dest)


if __name__ == "__main__":
    main()
