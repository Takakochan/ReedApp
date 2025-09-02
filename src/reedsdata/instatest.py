import csv
import datetime
import json
import time

import requests

# Business AccountのIDの入力．
# 注意：（me?fields=id,name）で出てきたものではない．忘れた場合は，
# https://accountscenter.instagram.com/profiles/
# でビジネスアカウントを選択すればURL欄に出てくる．
IG_USER_ID = "17841423293058655"
LONG_ACCESS_TOKEN = "EAARfzxDMs1MBOwFVCL8inacvFSt0IIE8nXEHWsTKBJLmJXNZCjwST0iCSMGgMT1XIKhDQici8yUiIr88yIyC6Hmq03GZBr4S48Wit6WsBd2fDuAZAlyZAwoxvNZAcuK7WRNI9GFGNsVSxqAjmLyZBspR6qwwPv4SvZAAOFfNyDA2LpWSbGace97wrxV2CGZAxPMnid4DuwUW0k3JDajB5sl11QZDZD"
# 一応短期トークンを使いたいなら↓のLONG_ACCESS_TOKENを書き換えて．

APP_INFO = {"INSTAGRAM_APP_NAME": "（備忘録的にアプリ名を入れておく）", "API_VERSION": "v19.0"}

ACCESS_TOKEN_TEST = LONG_ACCESS_TOKEN

URL_GRAPH_API_ROOT = "https://graph.facebook.com/" + APP_INFO[
    "API_VERSION"] + "/"
BASEURL_GET_HASHTAG_ID_BY_NAME = URL_GRAPH_API_ROOT + "ig_hashtag_search?"

# 投稿に関する欲しいfieldを入力しておく．
WANTED_FIELDS_LIST_BASE = [
    "id", "timestamp", "permalink", "media_product_type", "media_type",
    "comments_count", "caption"
]

# URLの組み立て．


def make_url_get_hashtag_id_by_name(hashtag_name,
                                    user_id=IG_USER_ID,
                                    access_token=ACCESS_TOKEN_TEST):

    url = BASEURL_GET_HASHTAG_ID_BY_NAME + "user_id=" + user_id
    url = url + "&access_token=" + access_token + "&q=" + hashtag_name
    return url


def make_url_get_posts_by_hashtag_id(hashtag_id,
                                     recent_or_top="recent",
                                     after=None,
                                     fields_list=WANTED_FIELDS_LIST_BASE,
                                     user_id=IG_USER_ID,
                                     access_token=ACCESS_TOKEN_TEST):

    fields_str = str(",".join(fields_list))
    print(fields_str)

    request_url = URL_GRAPH_API_ROOT + hashtag_id
    if recent_or_top == "top":
        request_url = request_url + "/top_media?"
    elif recent_or_top == "recent":
        request_url = request_url + "/recent_media?"
    else:
        # どちらでもなかったらとりあえずrecentで取る．
        request_url = request_url + "/recent_media?"
    request_url = request_url + f"user_id={user_id}&access_token={access_token}&fields={fields_str}"

    if after is not None:
        request_url = request_url + f"&after={str(after)}"

    result = request_url

    return result


# ハッシュタグIDの取得．
def get_hashtag_id_by_name(hashtag_name,
                           user_id=IG_USER_ID,
                           access_token=ACCESS_TOKEN_TEST):

    url = make_url_get_hashtag_id_by_name(hashtag_name=hashtag_name,
                                          user_id=user_id,
                                          access_token=access_token)
    print(url)
    response = requests.get(url)
    res_text = json.loads(response.text)
    print(res_text)

    if "error" in res_text.keys():
        print("response error")
        return None

    result = json.loads(response.text)["data"][0]["id"]
    result = str(result)
    print(result)

    return result
