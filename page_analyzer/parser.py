from bs4 import BeautifulSoup


def get_text_or_none(tag):
    if tag:
        return tag.get_text(strip=True)
    return None


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")

    h1 = get_text_or_none(soup.find("h1"))
    title = get_text_or_none(soup.find("title"))

    meta_description = soup.find("meta", attrs={"name": "description"})
    description = None

    if meta_description:
        description = meta_description.get("content")

    return {
        "h1": h1,
        "title": title,
        "description": description,
    }
