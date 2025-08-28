import requests
from data_models import Book

OPENLIBRARY_COVER_URL = "https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"


def get_book_cover(isbn, title, author) -> str:
    """
    Fetches a book cover image URL from the Open Library API.
    First tries to find the cover by ISBN, then by title and author search.
    :param isbn: ISBN of the book (with or without dashes)
    :param title: Title of the book
    :param author: Author name of the book
    :return: URL string of the book cover image, or empty string if not found
    """
    if isbn:
        isbn = str(isbn).replace("-", "").strip()
        url = f"https://openlibrary.org/isbn/{isbn}.json"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if "covers" in data and data["covers"]:
                print("cover by isbn")
                return OPENLIBRARY_COVER_URL.format(cover_id=data["covers"][0])

    if title:
        search_url = "https://openlibrary.org/search.json"
        params = {"title": title}
        response = requests.get(search_url, params=params)

        if response.status_code == 200:
            results = response.json().get("docs", [])

            for book in results:
                if "cover_i" in book:
                    if author:
                        # validate if the book is the right one, by checking the author too
                        if author in book.get("author_name", []):
                            print("cover by book search")
                            return OPENLIBRARY_COVER_URL.format(cover_id=book["cover_i"])
    print("No cover found")
    return ""