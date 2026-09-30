import csv
import os
import requests
from bs4 import BeautifulSoup


def run_scraper():
    print("--- STARTING SCRAPER ---")
    url = "http://books.toscrape.com/"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        print(f"1. Fetching data from: {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"2. Response status code: {response.status_code}")

        if response.status_code != 200:
            print("ERROR: Site responded with non-200 code!")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.find_all("article", class_="product_pod")
        print(f"3. Found {len(books)} books on the page.")

        scraped_data = []
        for book in books:
            title = book.h3.a["title"]
            price = book.find("p", class_="price_color").text.strip()
            scraped_data.append({"Title": title, "Price": price})

        if scraped_data:
            save_to_csv(scraped_data)
        else:
            print("ERROR: No books were scraped!")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")


def save_to_csv(data):
    filename = "scraped_books.csv"
    filepath = os.path.abspath(filename)
    print(f"4. Attempting to save CSV file to: {filepath}")

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Title", "Price"])
        writer.writeheader()
        writer.writerows(data)

    print(f"5. SUCCESS! Saved {len(data)} items to '{filename}'")


if __name__ == "__main__":
    run_scraper()