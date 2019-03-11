# -*- coding: utf-8 -*-
from datetime import datetime

from android_review_crawler import get_android_reviewFromeAuMarket, get_android_reviewFromGooglePlay
from ios_review_crawler import get_ios_review

if __name__ == "__main__":
    print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + " Android Review Crawler Started")
    print('Get reviews from au Market...')
    get_android_reviewFromeAuMarket()
    print('Get reviews from Google Play...')
    get_android_reviewFromGooglePlay()
    print
    print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + " iOS Review Crawler Started")
    print('Get reviews from App Store...')
    get_ios_review()
    print
