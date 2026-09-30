import csv
import re
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


class EmailScraperCrawler:

    def __init__(self, seed_url, max_pages=10):
        self.seed_url = seed_url
        self.domain = urlparse(seed_url).netloc
        self.max_pages = max_pages

        self.to_visit = [seed_url]
        self.visited = set()
        self.emails_found = set()

        # Regex pattern to detect valid email addresses
        self.email_pattern = re.compile(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        )

    def run(self):
        print(f"--- Starting Email Crawler on: {self.domain} ---")

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        while self.to_visit and len(self.visited) < self.max_pages:
            url = self.to_visit.pop(0)

            if url in self.visited:
                continue

            print(f"[{len(self.visited) + 1}/{self.max_pages}] Scanning: {url}")
            self.visited.add(url)

            try:
                response = requests.get(url, headers=headers, timeout=5)
                if "text/html" not in response.headers.get("Content-Type", ""):
                    continue

                # 1. SCRAPE: Extract all emails from page text and mailto links
                new_emails = set(self.email_pattern.findall(response.text))

                # Filter out junk image matches (e.g., image@2x.png)
                valid_emails = {
                    e
                    for e in new_emails
                    if not e.endswith(
                        (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")
                    )
                }

                if valid_emails:
                    print(f"   -> Found {len(valid_emails)} email(s): {valid_emails}")
                    self.emails_found.update(valid_emails)

                # 2. CRAWL: Extract internal links to find contact/about pages
                soup = BeautifulSoup(response.text, "html.parser")
                for link in soup.find_all("a", href=True):
                    abs_url = urljoin(url, link["href"]).split("#")[0]
                    link_domain = urlparse(abs_url).netloc

                    # Stay on the same domain and avoid non-http links
                    if (
                        link_domain == self.domain
                        and abs_url not in self.visited
                        and abs_url.startswith("http")
                    ):
                        self.to_visit.append(abs_url)

            except requests.RequestException as e:
                print(f"   -> Failed to load {url}: {e}")

        self.save_results()

    def save_results(self):
        filename = "found_emails.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Email Address"])
            for email in sorted(self.emails_found):
                writer.writerow([email])

        print(f"\n--- Complete! ---")
        print(f"Total unique emails found: {len(self.emails_found)}")
        print(f"Saved to '{filename}'")


if __name__ == "__main__":
    # Replace with your target website
    TARGET_SITE = "https://example.com"
    bot = EmailScraperCrawler(seed_url=TARGET_SITE, max_pages=15)
    bot.run()