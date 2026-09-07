import requests
from bs4 import BeautifulSoup

def scrape_titles(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        h1_tags = soup.find_all('h1')
        
        titles = [h1.get_text().strip() for h1 in h1_tags]
        return titles
    except Exception as e:
        return [f"Error: {e}"]

if __name__ == "__main__":
    target_url = "https://example.com"
    print(f"Scraping titles from: {target_url}")
    titles = scrape_titles(target_url)
    if titles:
        print("Found titles:")
        for title in titles:
            print(f"- {title}")
    else:
        print("No titles found or error occurred.")
