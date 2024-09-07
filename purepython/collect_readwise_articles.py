# from .fetch_readwise import fetch_from_export_api
import os
import datetime
import requests  # This may need to be installed from pip
from django.core.mail import send_mail

# token = 'XXX'
# token = os.getenv("READWISE_API_KEY", "")


def fetch_reader_document_list_api(token, updated_after=None, location=None):
    full_data = []
    next_page_cursor = None
    got_at_least_one_page = False
    while True:
        params = {}
        if next_page_cursor:
            params["pageCursor"] = next_page_cursor
        if updated_after:
            params["updatedAfter"] = updated_after
        if location:
            params["location"] = location
        print("Making export api request with params " + str(params) + "...")
        # assert False, token
        # try:
        response = requests.get(
            url="https://readwise.io/api/v3/list/",
            params=params,
            headers={"Authorization": f"Token {token}"},
            verify=False,
        )
        if response.status_code == 429:
            if got_at_least_one_page:
                # 429 is a throttling error
                # break assumes you don't actually need ALL the data
                # this will occassionally fail
                break
            else:
                raise Exception(
                    f"Request failed with status code {response.status_code}: {response.text}"
                )
        elif response.status_code != 200:
            raise Exception(
                f"Request failed with status code {response.status_code}: {response.text}"
            )
        # print(response.status_code)
        # response.raise_for_status()

        # except requests.exceptions.HTTPError as err:
        #     raise Exception(f"HTTP error occurred: {err}") from err

        # from pprint import pformat

        # assert False, pformat(response)
        # assert False, response.json()["results"]

        next_page_cursor = response.json().get("nextPageCursor")
        if not next_page_cursor:
            break
        full_data.extend(response.json()["results"])
        got_at_least_one_page = True
    return full_data


# def filter_summaries(full_data: list) -> list:
#     non_null_summaries = [d["summary"] for d in full_data if d["summary"]]
#     return non_null_summaries[:10]


# def is_language_article(summary: str) -> bool:
#     return "MASSIVE GATHERING" in summary


# def make_email_subject_and_body(summary: str) -> tuple:
#     return ("MASSIVE GATHERING", summary)


# def estimate_cefr_level(summary: str) -> bool:
#     return "MASSIVE GATHERING" in summary


# def send_digest_email(subject: str, body: str) -> None:
#     return None

from smtplib import SMTPServerDisconnected
from typing import Tuple


def collect_readwise_articles(
    token, updated_after=None, location=None, recipient_list=[], limit=50
) -> Tuple[int, int]:
    full_data = fetch_reader_document_list_api(
        token=token, updated_after=updated_after, location=location
    )
    # print("------------------------------------")
    # assert False, full_data[:10]
    # print("------------------------------------")
    # summaries = filter_summaries(full_data)
    success_count = 0
    fail_count = 0
    for article in full_data[:limit]:
        if article["summary"] and not article["title"].startswith("[summary]"):
            subject = "[summary] " + article["title"]
            body = article["summary"]

            success = False
            print(subject)
            while not success:
                try:
                    send_mail(
                        subject,
                        body,
                        "from@example.com",
                        recipient_list,
                        fail_silently=False,
                    )
                    success_count += 1
                    print("email sent")
                    success = True
                # except (SMTPServerDisconnected, TimeoutError):
                except:
                    fail_count += 1
                    print("email failed")
    return success_count, 0


# def fetch_reader_document_list_api2(updated_after=None, location=None):
#     response = requests.get(
#         url="https://readwise.io/api/v3/list/",
#         params={},
#         headers={"Authorization": f"Token {token}"},
#         verify=False,
#     )
#     return response.json()["results"]


if __name__ == "__main__":
    res = fetch_reader_document_list_api()
    print(res[0])
    print(len(res))

# Get all of a user's documents from all time
# all_data = fetch_reader_document_list_api()

# Get all of a user's archived documents
# archived_data = fetch_reader_document_list_api(location="archive")

# Later, if you want to get new documents updated after some date, do this:
# docs_after_date = datetime.datetime.now() - datetime.timedelta(
#     days=1
# )  # use your own stored date
# new_data = fetch_reader_document_list_api(docs_after_date.isoformat())
