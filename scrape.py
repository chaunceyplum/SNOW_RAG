import os
import json
import requests
from bs4 import BeautifulSoup
import re
import uuid

def fetch_snowflake_docs(url):
    """Fetch HTML content from a given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_links(html, base_url):
    """Extract relevant Snowflake documentation links from the page."""
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if href.startswith('/en/') and 'docs.snowflake.com' not in href:
            links.add(base_url + href)
    return links

def sanitize_filename(name):
    """Sanitize filenames by removing invalid characters and trimming the last character."""
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name).strip('_')[:100]
    sanitized_again = re.sub('[¶]','',sanitized)
    return sanitized_again

def parse_docs(html, url):
    """Parse Snowflake documentation page and extract structured content."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract page title
    title_tag = soup.find('h1')
    page_title = title_tag.get_text().strip() if title_tag else "Untitled"
    sanitized_title = sanitize_filename(page_title)

    sections = []
    current_section = {"section": page_title, "sectionId": str(uuid.uuid4()), "paragraphs": []}
    
    for element in soup.find_all(['h1', 'h2', 'h3', 'p']):
        if element.name in ['h1', 'h2', 'h3']:
            # Save the previous section if it has content
            if current_section["paragraphs"]:
                sections.append(current_section)
            # Start a new section
            current_section = {
                "section": element.get_text().strip(),
                "sectionId": str(uuid.uuid4()),
                "paragraphs": []
            }
        elif element.name == 'p' and element.get_text().strip():
            current_section["paragraphs"].append(element.get_text().strip())

    # Save the last section
    if current_section["paragraphs"]:
        sections.append(current_section)

    return {
        "guid": str(uuid.uuid4()),
        "title": page_title,
        "path": f"docs/{sanitized_title}.md",
        "fullText": "\n".join([" ".join(sec["paragraphs"]) for sec in sections]),
        "headers": [[h.name, h.get_text().strip()] for h in soup.find_all(['h1', 'h2', 'h3'])],
        "sections": sections,
        "url": url,
        "tags": generate_tags(page_title)
    }

def generate_tags(title):
    """Generate relevant tags based on title keywords."""
    keywords = title.lower().split()
    common_tags = ["SQL", "syntax", "query", "commands", "functions"]
    return list(set([word.capitalize() for word in keywords if word in common_tags]))

def save_page(page_data, output_dir="snowflake_docs"):
    """Save the extracted documentation data as JSON."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filename = f"{output_dir}/{page_data['title']}.json"
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(page_data, file, indent=4)
    print(f"Saved: {filename}")

def scrape_all_docs(start_url):
    """Scrape all documentation pages starting from the given URL."""
    base_url = "https://docs.snowflake.com"
    visited = set()
    to_visit = {start_url}
    
    while to_visit:
        current_url = to_visit.pop()
        if current_url in visited:
            continue
        print(f"Scraping: {current_url}")
        html = fetch_snowflake_docs(current_url)
        if html:
            try:
                visited.add(current_url)
                page_data = parse_docs(html, current_url)
                save_page(page_data)
                to_visit.update(extract_links(html, base_url))
            except Exception as e:
                print(f"Error processing {current_url}: {e}")
                continue  # Move to the next page on error

def main():
    start_url = "https://docs.snowflake.com"  # Update with the desired URL
    scrape_all_docs(start_url)

if __name__ == "__main__":
    main()
