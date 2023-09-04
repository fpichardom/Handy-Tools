import json
import time
import uuid
import random
import requests
from datetime import datetime
from requests.exceptions import HTTPError, RequestException
from typing import Dict, Any, Optional
import pandas as pd


from langdetect import detect
import unicodedata
import re
import spacy

import logging

# Helper functions 

def detect_language(text):
    try:
        lang = detect(text)
        if lang != 'es':
            return 'en'
        else:
            return 'es'
    except:
        return 'en'
    
nlp_en = spacy.load('en_core_web_sm')
nlp_es = spacy.load('es_core_news_sm')

def geo_locality_preprocess(text):
    # Detect language
    lang = detect_language(text)
    #print("Language detected: ", lang)
    text = unicodedata.normalize('NFKD', text)
    #print("Text normalized: ", text)
    # Add space around punctuation
    text = re.sub(r'([.,;])', r' \1 ', text)
    #print("Text with spaces around punctuation: ", text)
    # Tokenize and lemmatize
    if lang == 'en':
        doc = nlp_en(text)
    elif lang == 'es':
        doc = nlp_es(text)

    #for token in doc:
    tokens = [token.text.lower() for token in doc if not token.is_punct and not token.is_space]
    return lang, tokens

def parse_geolocate_debug_str(s):
    # handle non-string cases
    if not isinstance(s, str):
        return pd.DataFrame()

    # ignore strings that contain 'g3Match'
    if 'g3Match' in s:
        return pd.DataFrame()

    # split string into parts
    parts = s.split('|:')

    # split parts into keys and values and put into a dictionary
    data_dict = {}
    for part in parts:
        split_part = part.split('=')
        # check if the key exists
        if len(split_part) > 1:
            key, value = split_part
            # handle case where value contains ':' or '|'
            if key == 'KFID':
                data_dict[key] = value
            else:
                data_dict[key] = value
        else:
            # handle the case where the key doesn't exist
            data_dict[split_part[0]] = None

    # convert dictionary into a Series
    df = pd.Series(data_dict)
    
    return df

# Class Definitions

class GeoLocateAPI:
    BASE_URL = "http://geo-locate.org/webservices/geolocatesvcv2/glcwrap.aspx"
    MAX_ATTEMPTS = 3
    BASE_WAIT_TIME = 1  # In seconds
    MAX_WAIT_TIME = 32  # In seconds

    def __init__(
        self,
        query_field="",
        country_field="",
        state_field="",
        key_field="",
        language = 0
    ):
        self.base_url = GeoLocateAPI.BASE_URL
        self.query_field = query_field
        self.country_field = country_field
        self.state_field = state_field
        self.key_field = key_field
        self.last_entry = None
        self.last_geolocate_raw_results = None
        self.language = language

    def search_geolocate(self, query: str, country: str = "", state: str = "", lang: int = 0) -> Optional[Dict[str, Any]]:
        """
        Searches the geolocation of the given query using the GeoLocate API.
        """
        params = {
            "locality": query,
            "country": country,
            "state": state,
            "enableH2O": 'false',
            "doPoly": "true",
            "displacePoly": "false",
            "languageKey": lang,
            "fmt": "geojson"
        }
 

        attempt = 1
        error = None
        while attempt <= GeoLocateAPI.MAX_ATTEMPTS:
            try:
                geolocate_response = requests.get(self.base_url, params)
                return geolocate_response.json()
            except (json.decoder.JSONDecodeError, HTTPError, RequestException) as e:
                error = e
                if attempt == GeoLocateAPI.MAX_ATTEMPTS:
                    break

                logging.error(f"Exception: {e}, Attempt: {attempt}, Query: {query}")

                sleep_time = min(
                    GeoLocateAPI.BASE_WAIT_TIME * (2 ** (attempt - 1)) + random.uniform(0, 0.1 * (2 ** attempt)),
                    GeoLocateAPI.MAX_WAIT_TIME,
                )
                time.sleep(sleep_time)
                attempt += 1

        return {"error": f"Failed to geolocate {query} after {attempt} attempts.", "exception": str(error)}
    
    
    def get_data(self, entry):
        """
        Gets the geolocation data of the given entry.
        """
        
        self.last_entry = entry
        self.last_geolocate_raw_results = self.search_geolocate(
            entry[self.query_field], country=entry[self.country_field], state=entry.get(self.state_field, None), lang=self.language
        )
        return self.last_geolocate_raw_results
    
    
    def format_results(self):
        if not self.last_entry or not self.last_geolocate_raw_results:
            return None
        
        formatted_results = {
            "download_history": {
                "download_date": datetime.today(),
                "download_uuid": str(uuid.uuid1()),
            },
            "keys": self.last_entry[self.key_field],
            #"keys": self.last_entry[self.key_field].split("|"),
            "data": self.last_entry,
            "geolocate_geo_result": self.last_geolocate_raw_results,
        }
        return formatted_results