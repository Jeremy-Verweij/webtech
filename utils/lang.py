import glob
import json

languages = {}
lang_names = {}

default_lang = "en"

def load_lang():
    language_list = glob.glob("local/*.json")
    for lang in language_list:
        filename = lang.split('\\')
        lang_code = filename[1].split('.')[0]
        with open(lang, 'r', encoding='utf8') as file:
            languages[lang_code] = json.loads(file.read())
            
    load_lang_names()
            
def load_lang_names():
    for lang_unlocal, lang in languages.items():
        lang_names[lang_unlocal] = lang['lang']

def get_lang(lang):
    lang = lang.lower()
    
    if languages[lang]:
        return languages[lang]
    return languages[default_lang]

load_lang()