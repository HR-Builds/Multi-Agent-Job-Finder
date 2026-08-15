from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

REQUEST_TIMEOUT = 15

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/151.0.0.0 Safari/537.36"
)


# ---------------------------------------------------------
# Helper: Validate URL
# ---------------------------------------------------------

def validate_url(url: str) -> bool:
    """Validate that the provided URL is HTTP/HTTPS."""

    try:
        parsed = urlparse(url)

        return parsed.scheme in ("http", "https") and bool(parsed.netloc)

    except Exception:
        return False


# ---------------------------------------------------------
# Helper: Clean HTML
# ---------------------------------------------------------

def clean_page_content(html: str) -> str:
    """
    Convert HTML into clean text.

    Removes unnecessary page elements such as:
    scripts, styles, navigation, ads, etc.
    """

    soup = BeautifulSoup(html, "html.parser")

    # Remove unnecessary elements
    for element in soup(
        [
            "script",
            "style",
            "noscript",
            "svg",
            "nav",
            "footer",
            "header",
            "aside",
            "form",
        ]
    ):
        element.decompose()

    text = soup.get_text(separator="\n")

    # Clean individual lines
    lines = []

    for line in text.splitlines():

        line = " ".join(line.split())

        if line:
            lines.append(line)

    # Remove duplicate consecutive lines
    cleaned_lines = []

    for line in lines:

        if not cleaned_lines or line != cleaned_lines[-1]:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


# ---------------------------------------------------------
# scrape_url Tool
# ---------------------------------------------------------

@tool
def scrape_url(url: str) -> str:
    """
    Scrape a webpage and return clean textual content.

    This tool is intended for extracting job posting content
    from publicly accessible job pages.
    """

    if not validate_url(url):
        return f"Invalid URL: {url}"

    try:

        response = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENT
            },
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )

        response.raise_for_status()

    except requests.RequestException as e:

        return (
            f"Unable to scrape URL.\n"
            f"URL: {url}\n"
            f"Error: {str(e)}"
        )

    # -----------------------------------------------------
    # Extract page content
    # -----------------------------------------------------

    content = clean_page_content(response.text)

    if not content.strip():

        return (
            f"No readable content found.\n"
            f"URL: {response.url}"
        )

    # -----------------------------------------------------
    # Limit content
    # -----------------------------------------------------
    #
    # Important for Gemini token usage.
    # We don't send extremely large pages to the LLM.
    #

    MAX_CONTENT_LENGTH = 12000

    if len(content) > MAX_CONTENT_LENGTH:

        content = content[:MAX_CONTENT_LENGTH]

        content += (
            "\n\n[Page content truncated for efficiency.]"
        )

    # -----------------------------------------------------
    # Return scraped content
    # -----------------------------------------------------

    return (
        f"URL: {response.url}\n\n"
        f"PAGE CONTENT:\n"
        f"{content}"
    )