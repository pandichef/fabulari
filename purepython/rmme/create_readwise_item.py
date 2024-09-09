# # UNDER CONSTRUCTION
# # THIS IS AN ALTERNATIVE TO EMAIL
# # I'M CURRENTLY USING EMAIL
# import requests


# def create_readwise_item(
#     token, title, body_in_html, url="https://yourapp.com#document1"
# ):
#     params = {
#         "url": url,
#         "html": body_in_html,
#         "should_clean_html": True,
#         "title": title,
#         "author": "fabulari",
#         "summary": "The document is itself a summary",
#         "location": "feed",
#         "category": "article",
#         "tags": ["summary"],
#     }
#     # if url:
#     #     params["url"] = url

#     res = requests.post(
#         url="https://readwise.io/api/v3/save/",
#         headers={"Authorization": f"Token {token}"},
#         json=params,
#     )
#     return res
