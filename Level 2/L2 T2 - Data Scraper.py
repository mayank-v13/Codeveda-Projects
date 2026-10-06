import csv
from bs4 import BeautifulSoup
import requests

# 1. Define target URL and headers to simulate a real browser request
url = "https://news.ycombinator.com/"
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

try:
    # 2. Retrieve web page content using requests
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # Check for successful response (HTTP 200)

    # 3. Parse HTML content with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    scraped_data = []

    # 4. Extract specific data (article title and link)
    articles = soup.select("tr.athing")
    for article in articles:
        title_element = article.select_one("span.titleline > a")
        if title_element:
            title = title_element.get_text(strip=True)
            link = title_element.get("href")

            scraped_data.append({"Title": title, "Link": link})

    # 5. Save the scraped data into a CSV file
    csv_filename = "news_headlines.csv"
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Title", "Link"])
        writer.writeheader()
        writer.writerows(scraped_data)

    print(
        f"Successfully extracted {len(scraped_data)} headlines and saved to '{csv_filename}'."
    )

except requests.exceptions.RequestException as e:
    print(f"Error fetching page content: {e}")