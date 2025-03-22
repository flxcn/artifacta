import requests
from bs4 import BeautifulSoup
import re

WIKIPEDIA_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"

def get_wikipedia_url(term):
    response = requests.get(WIKIPEDIA_API + term)
    return response.url if response.status_code == 200 else None

def hyperlink_terms(html_content, terms):
    soup = BeautifulSoup(html_content, "html.parser")
    text_nodes = soup.find_all(text=True)
    
    for node in text_nodes:
        parent = node.parent
        if parent.name not in ["script", "style", "a"]:  # Avoid modifying links/scripts
            new_text = node
            for term in terms:
                wiki_url = get_wikipedia_url(term)
                if wiki_url:
                    new_text = re.sub(
                        rf"\b({re.escape(term)})\b",
                        rf'<a href="{wiki_url}" target="_blank">\1</a>',
                        new_text,
                        flags=re.IGNORECASE
                    )
            node.replace_with(BeautifulSoup(new_text, "html.parser"))

    return str(soup)

# Example Usage
url = "https://example.com"  # Replace with your target page
response = requests.get(url)
terms = ["Python", "Machine Learning", "JavaScript"]
updated_html = hyperlink_terms(response.text, terms)

# Save or display modified HTML
with open("output.html", "w", encoding="utf-8") as file:
    file.write(updated_html)

print("Updated HTML saved to output.html")
