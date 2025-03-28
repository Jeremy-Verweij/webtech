import glob
import json

from flask import session

from models import Settings
from setup import db

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

def get_user_language():
    if "language" in session:
        return session["language"]

    if "user_id" in session:
        lang = (
            db.session.query(Settings.Language)
            .where(Settings.UserId == session["user_id"])
            .one_or_none()
        )
        if lang:
            session["language"] = lang

        return session["Language"] if lang else default_lang  # Default to English

    return default_lang  # Default for guests

load_lang()