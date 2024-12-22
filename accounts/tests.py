import os
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


# Function to download files and save them in respective folders
def download_file(url, folder):
    # Get the content of the file
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Extract the file name from the URL
        filename = os.path.basename(urlparse(url).path)
        filepath = os.path.join(folder, filename)

        # Write the content to a local file
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Downloaded {filename} to {folder}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")


# Function to create folders if they don't exist
def create_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


# Function to extract and download all images, CSS, and JS files from the HTML page
def scrape_files_from_html(html_url, base_url):
    # Fetch the HTML content from the URL
    try:
        response = requests.get(html_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Error fetching HTML from {html_url}: {e}")
        return

    # Create directories for images, svg, css, and js
    create_folder("images")
    create_folder("svg")
    create_folder("css")
    create_folder("js")

    # Find all image tags and download the source files
    for img_tag in soup.find_all("img"):
        img_url = img_tag.get("src")
        if img_url:
            img_url = urljoin(base_url, img_url)  # Convert relative URL to absolute
            # Check if the image is an SVG, otherwise save in 'images'
            if img_url.lower().endswith(".svg"):
                download_file(img_url, "svg")
            else:
                download_file(img_url, "images")

    # Find all link tags for CSS files and download
    for link_tag in soup.find_all("link", {"rel": "stylesheet"}):
        css_url = link_tag.get("href")
        if css_url:
            css_url = urljoin(base_url, css_url)  # Convert relative URL to absolute
            download_file(css_url, "css")

    # Find all script tags and download the JS files
    for script_tag in soup.find_all("script"):
        js_url = script_tag.get("src")
        if js_url:
            js_url = urljoin(base_url, js_url)  # Convert relative URL to absolute
            download_file(js_url, "js")


# Example usage
html_url = "https://tresto-admin-template.multipurposethemes.com/bs5/template/vertical/main/index-8.html"  # Remote URL
base_url = "https://tresto-admin-template.multipurposethemes.com/bs5/template/vertical/main/"  # Base URL for resource files

scrape_files_from_html(html_url, base_url)
