from pprint import pprint
from langdetect import detect
import os
import datetime
import requests  # This may need to be installed from pip

token = os.getenv("READWISE_API_KEY", "")


def fetch_from_export_api(updated_after=None, token=token):
    # Ref https://readwise.io/api_deets
    full_data = []
    next_page_cursor = None
    while True:
        params = {}
        if next_page_cursor:
            params["pageCursor"] = next_page_cursor
        if updated_after:
            params["updatedAfter"] = updated_after
        print("Making export api request with params " + str(params) + "...")
        response = requests.get(
            url="https://readwise.io/api/v2/export/",
            params=params,
            headers={"Authorization": f"Token {token}"},
            verify=False,
        )
        full_data.extend(response.json()["results"])
        next_page_cursor = response.json().get("nextPageCursor")
        if not next_page_cursor:
            break
    return full_data


"""
# Get all of a user's books/highlights from all time
all_data = fetch_from_export_api()

# Later, if you want to get new highlights updated since your last fetch of allData, do this.
last_fetch_was_at = datetime.datetime.now() - datetime.timedelta(
    days=1
)  # use your own stored date
new_data = fetch_from_export_api(last_fetch_was_at.isoformat())

# print(all_data[0])
"""


def make_digest(all_data):
    digest_list = []
    for article in all_data:
        for note in article["highlights"]:
            text = note["text"]
            language = detect(text)
            if language in ["es", "he", "ar"] and len(text.split()) < 5:
                digest_list.append((note["text"], language))
    return digest_list


# pprint(make_digest(all_data))
