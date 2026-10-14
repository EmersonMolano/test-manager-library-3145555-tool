import os
import sys
from datetime import datetime

import requests


BASE_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
USERNAME = os.getenv("ADMIN_USERNAME", "admin")
PASSWORD = os.getenv("ADMIN_PASSWORD", "change-me-now")


def call(method, path, token, **kwargs):
    response = requests.request(method, f"{BASE_URL}{path}", headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}, timeout=20, **kwargs)
    if response.status_code >= 400:
        raise RuntimeError(f"{method} {path}: {response.status_code} {response.text}")
    return response.json() if response.content else None


def main():
    login = requests.post(f"{BASE_URL}/auth/login", json={"username": USERNAME, "password": PASSWORD}, timeout=20)
    login.raise_for_status()
    token = login.json()["access_token"]
    categories = call("GET", "/categories", token)
    category_ids = [category["id"] for category in categories]

    books = []
    stamp = datetime.now().strftime("%m%d%H%M")
    for index in range(40):
        payload = {"title": f"Demonstration Book {stamp}-{index + 1}", "author": f"Library Author {index + 1}", "isbn": f"978000{stamp}{index:03d}"[-13:], "category_id": category_ids[index % len(category_ids)], "total_copies": 4}
        books.append(call("POST", "/books", token, json=payload))

    members = []
    for index in range(10):
        members.append(call("POST", "/members", token, json={"full_name": f"Demonstration Member {stamp}-{index + 1}", "document_number": f"DEMO-{stamp}-{index + 1}"}))

    loans = []
    for index in range(15):
        member = members[index % len(members)]
        book = books[index]
        loans.append(call("POST", "/loans", token, json={"member_id": member["id"], "items": [{"book_id": book["id"]}]}))

    print(f"Seeded {len(books)} books, {len(members)} members and {len(loans)} loans through the API.")
    print("Three overdue examples will appear after their 14-day due date; the API intentionally does not expose a time-travel shortcut.")


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as error:
        print(f"API connection failed: {error}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
