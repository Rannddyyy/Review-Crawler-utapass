# -*- coding: utf-8 -*-
import traceback

import googletrans


class Translator:
    bearer_token = ''

    def __init__(self):
        pass

    def GetTextAndTranslateFromGoogle(self, source_lang, target_lang, text):
        translator = googletrans.Translator()
        try:
            result = translator.translate(text, dest=target_lang).text
        except Exception:
            print(traceback.format_exc())
            return 'Translation failed.'
        return result
