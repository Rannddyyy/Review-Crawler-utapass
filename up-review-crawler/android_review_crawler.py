# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from MongoManager import MongoManager
from RequestManager import RequestManager
from UtaTranslator import Translator

REVIEW_COUNT_LIMIT = 8
FOOTER = ['au Market reviews crawler', 'Google Play reviews crawler']
FOOTER_ICON = ['https://img.au-market.com/mapi/pc_icon/39767/3976700000002/100211_116788.png',
               'https://cdn4.iconfinder.com/data/icons/free-colorful-icons/360/google_play.png']
BEFORE_DAY = 2


def match_class(target):
    def do_match(tag):
        classes = tag.get('class', [])
        return all(c in classes for c in target)

    return do_match


def get_json(text):
    t1 = text[text.index('{'):]
    t2 = t1[::-1]
    t3 = t2[t2.index('}'):]
    return t3[::-1]


def send_message(comments, footer, footer_icon):
    star = ":star:"
    data = {
        'score': comments['score'],
        'title': comments['title'],
        'date': comments['date'],
        'comment': comments['comment'],
        'pretext': '`TEST` UtaPass Android has a new review!',
        'text': ''.join(star * int(comments['score']) + ' Score : %s' % str(comments['score'])),
        'content': u'{}\n\n [Translation]\n*{}*\n\n{}\n\n_{}  ver.{}_'.format(comments['comment'],
                                                                              comments['translated_title'],
                                                                              comments['translated_comment'],
                                                                              (comments['date']).strftime('%Y-%m-%d'),
                                                                              comments['version']),
        'thumb_url': 'https://img.au-market.com/mapi/pc_icon/39767/3976700000002/100211_116788.png',
        'footer': footer,
        'footer_icon': footer_icon
    }
    # if review has no version info or from au Market, wouldn't show comments['version']
    if comments['version'] is None or footer == FOOTER[0]:
        data['content'] = u'{}\n\n [Translation]\n*{}*\n\n{}\n\n_{}_'.format(comments['comment'],
                                                                             comments['translated_title'],
                                                                             comments['translated_comment'],
                                                                             (comments['date']).strftime('%Y-%m-%d'))
    RequestManager().slackAttachmentsWithFieldsMessager('#test-b0t', data['pretext'], "", data['text'], "", "",
                                                        "Android Reviews Bot", data['footer'], data['title'],
                                                        data['content'], data['thumb_url'], data['footer_icon'])
    # send review to up_qa-happytime
    # RequestManager().slackAttachmentsWithFieldsMessager('#up_qa-happytime', data['pretext'], "", data['text'], "", "",
    #                                                     "Android Reviews Bot", data['footer'], data['title'],
    #                                                     data['content'], data['thumb_url'], data['footer_icon'])


def get_android_reviewFromeAuMarket():
    db = MongoManager()
    translator = Translator()
    comment_info = {
        "title": "",
        "translated_title": "",
        "score": 0.0,
        "date": "",
        "comment": "",
        "translated_comment": "",
        "version": None
    }
    url = 'https://pass.auone.jp/app/detail/review/list?app_id=3976700000002&sort=post&display_ver=new&page_num=1'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Mobile Safari/537.36'
    }

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")
    rows = soup.find_all(match_class(["t-media__body"]))
    review_count = 0
    for row in rows:
        if len(row.contents) >= 7:
            # get comment's title
            comment_info["title"] = row.contents[1].contents[1].contents[0].strip()
            # get comment's score
            comment_info["score"] = float(row.contents[3].contents[3].contents[0].strip())
            # get comment date
            comment_info["date"] = datetime.strptime(row.contents[3].contents[5].contents[0].strip(), "%Y/%m/%d")
            # get comments ; check comment is partial visible (items len = 9) or all visible (items len = 7)
            comment = ""
            if len(row.contents) == 9:
                for i in range(0, len(row.contents[7].contents), 2):
                    comment = comment + row.contents[7].contents[i].strip()
                comment_info["comment"] = comment
            else:
                for i in range(0, len(row.contents[5].contents), 2):
                    comment = comment + row.contents[5].contents[i].strip()
                comment_info["comment"] = comment

            # help sender stop
            if review_count >= REVIEW_COUNT_LIMIT:  # when sent up to 5 reviews
                print('>>>> Limited reviews count.')
                break

            if not db.query_is_comments_existed("android_au", comment_info):
                db.insert_reviews("android_au", comment_info)
                comment_info["translated_title"] = translator.GetTextAndTranslateFromGoogle('ja', 'zh-TW',
                                                                                            comment_info["title"])
                comment_info["translated_comment"] = translator.GetTextAndTranslateFromGoogle('ja', 'zh-TW',
                                                                                              comment_info["comment"])
                # would not send msg when it's datetime before {BEFORE_DAY}
                if datetime.now() - comment_info['date'] < timedelta(days=BEFORE_DAY):
                    send_message(comment_info, FOOTER[0], FOOTER_ICON[0])  # post message to slack
                    review_count += 1
    print('>>>> ' + str(review_count) + ' reviews be sent.')


def get_android_reviewFromGooglePlay():
    db = MongoManager()
    translator = Translator()
    comment_info = {
        "title": "",
        "translated_title": "",
        "score": 0.0,
        "date": "",
        "comment": "",
        "translated_comment": "",
        "version": None
    }

    url = 'https://play.google.com/_/PlayStoreUi/data?ds.extension=136880256&f.sid=-6639796089229955814&hl=ja&bl=boq_playuiserver_20180731.12_p0&soc-app=121&soc-platform=1&soc-device=1&authuser&_reqid=245019&rt=c'
    headers = {
        u'Content-Type': u'application/x-www-form-urlencoded;charset=utf-8'
    }
    payload = {
        u'f.req': u'[[[136880256,[{"136880256":[null,null,[2,2,[40,null]],["com.kddi.android.UtaPass",7]]}],null,null,0]]]'}

    req = requests.post(url, data=payload, headers=headers).text
    json_dict = json.loads(get_json(req))
    review_count = 0
    key = list(json_dict.keys())[0]
    if len(json_dict[key]) == 0:
        print('>>>> There has no review data.')
        return
    for i in range(len(json_dict[key][0])):
        # get comment's title
        comment_info["title"] = json_dict[key][0][i][1][0]
        # get comment's score
        comment_info["score"] = json_dict[key][0][i][2]
        # get comment date
        comment_info["date"] = datetime.fromtimestamp(json_dict[key][0][i][5][0])
        # get comments
        comment_info['comment'] = json_dict[key][0][i][4]
        # get version
        comment_info['version'] = json_dict[key][0][i][10]

        # help sender stop 
        if review_count >= REVIEW_COUNT_LIMIT:  # when sent up to 5 reviews
            print('>>>> Limited reviews count.')
            break

        if not db.query_is_comments_existed("android_gp", comment_info):
            db.insert_reviews("android_gp", comment_info)
            comment_info["translated_title"] = translator.GetTextAndTranslateFromGoogle('ja', 'zh-TW',
                                                                                        comment_info["title"])
            comment_info["translated_comment"] = translator.GetTextAndTranslateFromGoogle('ja', 'zh-TW',
                                                                                          comment_info["comment"])
            # would not send msg when it's datetime before {BEFORE_DAY}
            if datetime.now() - comment_info['date'] < timedelta(days=BEFORE_DAY):
                send_message(comment_info, FOOTER[1], FOOTER_ICON[1])  # post message to slack
                review_count += 1
    print('>>>> ' + str(review_count) + ' reviews be sent.')


if __name__ == "__main__":
    print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + " Android Review Crawler Started")
    print('Get reviews from au Market...')
    get_android_reviewFromeAuMarket()
    print('Get reviews from Google Play...')
    get_android_reviewFromGooglePlay()
    print
