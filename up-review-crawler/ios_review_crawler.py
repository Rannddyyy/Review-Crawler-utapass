# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import feedparser

from MongoManager import MongoManager
from RequestManager import RequestManager
from UtaTranslator import Translator

REVIEW_COUNT_LIMIT = 5
BEFORE_DAY = 2


def send_message(comments):
    star = ":star:"
    data = {
        'score': comments['score'],
        'title': comments['title'],
        'date': comments['date'],
        'comment': comments['comment'],
        'pretext': '`TEST` UtaPass iOS has a new review!',
        'text': ''.join(star * int(comments['score']) + ' Score : %s' % str(comments['score'])),
        'content': u'{}\n\n [Translation]\n*{}*\n\n{}\n\n_{}  ver.{}_'.format(comments['comment'],
                                                                              comments['translated_title'],
                                                                              comments['translated_comment'],
                                                                              (comments['date']).strftime('%Y-%m-%d'),
                                                                              comments['version']),
        'thumb_url': 'https://img.au-market.com/mapi/pc_icon/39767/3976700000002/100211_116788.png',
        'footer': 'App Store reviews crawler',
        'footer_icon': 'https://banner2.kisspng.com/20180729/cup/kisspng-app-store-iphone-apple-app-store-icon-transparent-5b5e1adc964cf5.4117097315328939166156.jpg',
    }
    RequestManager().slackAttachmentsWithFieldsMessager('#test-b0t', data['pretext'], "", data['text'], "", "",
                                                        "iOS Reviews Bot", data['footer'], data['title'],
                                                        data['content'], data['thumb_url'], data['footer_icon'])
    # send review to up_qa-happytime
    # RequestManager().slackAttachmentsWithFieldsMessager('#up_qa-happytime', data['pretext'], "", data['text'], "", "",
    #                                                     "iOS Reviews Bot", data['footer'], data['title'],
    #                                                     data['content'], data['thumb_url'], data['footer_icon'])


def get_ios_review():
    db = MongoManager()
    translator = Translator()
    comment_info = {
        "title": "",
        "translated_title": "",
        "score": 0.0,
        "date": "",
        "comment": "",
        "translated_comment": "",
        "version": 0.0
    }
    url = 'https://itunes.apple.com/jp/rss/customerreviews/page=1/id=579510737/sortby=mostrecent/xml'

    feed = feedparser.parse(url)
    review_count = 0
    for entry in feed.entries[1:]:
        # get comment's title
        comment_info["title"] = entry['title']
        # get comment's score
        comment_info["score"] = entry['im_rating']
        # get comment date
        comment_info["date"] = datetime.strptime(entry['updated'], "%Y-%m-%dT%H:%M:%S-07:00")
        # get comments
        comment_info['comment'] = entry['content'][0]['value']
        # get version
        comment_info['version'] = entry['im_version']

        # help sender stop
        if review_count >= REVIEW_COUNT_LIMIT:  # when sent up to 5 reviews
            print('>>>> Limited reviews count.')
            break

        if not db.query_is_comments_existed("ios", comment_info):
            db.insert_reviews("ios", comment_info)
            comment_info["translated_title"] = translator.GetTextAndTranslateFromGoogle('ja', 'zh-TW',
                                                                                        comment_info["title"])
            comment_info["translated_comment"] = translator.GetTextAndTranslateFromGoogle('ja', 'zh-TW',
                                                                                          comment_info["comment"])
            # would not send msg when it's datetime before {BEFORE_DAY}
            if datetime.now() - comment_info['date'] < timedelta(days=BEFORE_DAY):
                send_message(comment_info)  # post message to slack
                review_count += 1

    print('>>>> ' + str(review_count) + ' reviews be sent.')
