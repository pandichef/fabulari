from pprint import pprint

# from langdetect import detect
from .gptsrs import detect_language_code as detect
import os
import datetime
import requests  # This may need to be installed from pip

# token = os.getenv("READWISE_API_KEY", "")


def fetch_from_export_api(token, updated_after=None) -> list:
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
        if response.status_code != 200:
            raise Exception(
                f"Request failed with status code {response.status_code}: {response.text}"
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

from typing import Tuple, List


def filter_phrases(all_data: list, max_phrase_length=4) -> List[str]:
    digest_list = []
    for article in all_data:
        for note in article["highlights"]:
            text = note["text"]
            if len(text.split()) <= max_phrase_length:
                digest_list.append(text)
    return digest_list


import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_language_codes(phrases: List[str]) -> List[str]:
    results = [None] * len(phrases)  # Pre-allocate the list with None to preserve order
    with ThreadPoolExecutor() as executor:
        # Submit all tasks to the executor, along with their index
        futures = {executor.submit(detect, phrases[i]): i for i in range(len(phrases))}

        # Process each completed task
        for future in as_completed(futures):
            index = futures[future]  # Get the index of the corresponding task
            try:
                results[
                    index
                ] = future.result()  # Place the result in the correct position
            except Exception as exc:
                print(f"An error occurred for phrase at index {index}: {exc}")
    return results


def make_digest_multithreaded(
    all_data: list, supported_languages=["es"]
) -> List[Tuple[str, str]]:
    phrases = filter_phrases(all_data)
    language_codes = get_language_codes(phrases)
    zipped_list = list(zip(phrases, language_codes))
    filtered_list = [
        (phrase, lang) for phrase, lang in zipped_list if lang in supported_languages
    ]
    return filtered_list


def make_digest(all_data: dict, supported_languages=["es"]) -> List[Tuple[str, str]]:
    # NO LONGER USED
    # NOW USE MULTITHREADED VERSION
    digest_list = []
    for article in all_data:
        for note in article["highlights"]:
            text = note["text"]
            # if len(text) < 100:
            #     print(text)
            this_language_code = detect(text)
            # if len(text) < 100:
            #     print(this_language_code)
            if this_language_code in supported_languages and len(text.split()) < 5:
                digest_list.append((text, this_language_code))
    return digest_list


# pprint(make_digest(all_data)
