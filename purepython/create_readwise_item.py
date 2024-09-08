# UNDER CONSTRUCTION
# THIS IS AN ALTERNATIVE TO EMAIL
# I'M CURRENTLY USING EMAIL
import requests


def create_readwise_item(token):
    res = requests.post(
        url="https://readwise.io/api/v3/save/",
        headers={"Authorization": f"Token {token}"},
        json={
            "url": "https://medium.com/coinmonks/bitcoin-pain-on-the-menu-78ef60c0901a",
            # No html is provided, so the url will be scraped to get the document's content.
            # "tags": ["tag3", "tag4"],
            "location": "feed",
        },
    )
    return res
