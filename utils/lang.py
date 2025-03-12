import glob
import json

languages = {}

default_lang = "en"

def load_lang():
    language_list = glob.glob("local/*.json")
    for lang in language_list:
        filename = lang.split('\\')
        lang_code = filename[1].split('.')[0]
        with open(lang, 'r', encoding='utf8') as file:
            languages[lang_code] = json.loads(file.read())

def get_lang(lang):
    lang = lang.lower()
    
    if languages[lang]:
        return languages[lang]
    return languages[default_lang]

def get_all_lang():
    return list(languages.keys())

load_lang()