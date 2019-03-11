# -*- coding: utf-8 -*-
import json
import os
import pickle
import requests
import time
from datetime import datetime
from json import JSONEncoder


class RequestManager:
    CONST_API_SLACK_HOOK = os.environ.get('SLACK_HOOK_CRAWLER')

    def __init__(self):
        pass

    def slackAttachmentsWithFieldsMessager(self, channel, pretext, title, text, title_link, attach_link, botname,
                                           footer, bold_text=None, field_content=None, thumb_url=None, footer_icon=None,
                                           icon_emoji=None):
        payload = {"channel": channel,
                   "attachments": [
                       {
                           "fallback": "",
                           "color": "#ffaa00",
                           "pretext": pretext,
                           "author_name": "",
                           "author_link": "",
                           "author_icon": "",
                           "title": title,
                           "title_link": title_link,
                           "text": text,
                           "fields": [
                               {
                                   "title": bold_text,
                                   "value": field_content,
                                   "short": False
                               }
                           ],
                           "image_url": attach_link,
                           "thumb_url": thumb_url,
                           "footer": footer,
                           "footer_icon": footer_icon,
                           "ts": time.mktime(datetime.now().timetuple())
                       }],
                   "username": botname,
                   "icon_emoji": icon_emoji,
                   "link_names": 1}

        req = requests.post(self.CONST_API_SLACK_HOOK, data=json.dumps(payload, cls=PythonObjectEncoder))
        print('slackAttachmentsWithFieldsMessager()  Response: ' + req.text)


class PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, unicode, int, float, bool, type(None))):
            return JSONEncoder.default(self, obj)
        return {'_python_object': pickle.dumps(obj)}
