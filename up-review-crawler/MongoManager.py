# -*- coding: utf-8 -*-
import os
from pymongo import MongoClient


class MongoViews:
    MONGO_VIEW_ANDROID_REVIEWS_AU = "android_reviews_aumarket"
    MONGO_VIEW_ANDROID_REVIEWS_GP = "android_reviews_googleplay"
    MONGO_VIEW_IOS_REVIEWS = "ios_review"


class MongoManager:
    DBURL = os.environ.get('MONGODB_URL')

    client = None
    db = None

    def __init__(self):
        self.client = MongoClient()
        # self.client = MongoClient(self.DBURL)
        self.db = self.client['upDashBoard']

    def query_is_comments_existed(self, view, data):
        col = get_collection(view)
        collection = self.db[col]
        result = collection.find_one({"score": data["score"],
                                      "title": data["title"],
                                      "createdDate": data["date"],
                                      "comment": data["comment"],
                                      "version": data["version"]
                                      })
        return result is not None

    def insert_reviews(self, view, data):
        col = get_collection(view)
        collection = self.db[col]
        result = collection.insert_one(
            {
                "title": data['title'],
                "score": data['score'],
                "createdDate": data['date'],
                "comment": data["comment"],
                "version": data["version"]
            })
        print result


def get_collection(view):
    if view == 'ios':
        return MongoViews.MONGO_VIEW_IOS_REVIEWS
    elif view == 'android_au':
        return MongoViews.MONGO_VIEW_ANDROID_REVIEWS_AU
    else:
        return MongoViews.MONGO_VIEW_ANDROID_REVIEWS_GP
