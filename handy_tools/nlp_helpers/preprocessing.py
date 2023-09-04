import os
from pypdf import PdfReader
import spacy
import gensim
import pandas as pd
import numpy as np
import re
#from langdetect import detect
import unicodedata


def convert_local_pdf_files2text(filenames, base_path):
    documents = []
    bad_files = []
    for index, filename in enumerate(filenames):
        doc = ""
        try:
            reader = PdfReader(os.path.join(base_path, filename))
            for page in reader.pages:
                doc+= page.extract_text()
        except Exception as e:
            bad_files.append((index, filename,))
            print(e)
        documents.append(doc)
    return documents, bad_files


def preprocess_text(text, aslist=True, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'], disable_parser_ner=False):
    
    if disable_parser_ner:
        nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
    else:
        nlp = spacy.load('en_core_web_sm')

    # Setting maximum number of tokens that the nlp model can handle. Default is 1,000,000 but increased here because large documents.    
    nlp.max_length = 4000000  # or whatever value you think is appropriate

    # Line breaks replaced by space because if replaced by nothing, words get concatenated.
    text = text.lower().replace('\n', ' ')

    doc = nlp(text)

    # Lemmatizing the text and removing punctuation, spaces, stop words and tokens with length less than 3 characters.
    tokens = [token for token in doc if not token.is_stop and not token.is_punct and not token.is_space and len(token.lemma_) > 3]
    
    # Checks if the allowed_postags atribute in the function call is not empty. If it is not empty, it filters the tokens by the allowed postags.
    if len(allowed_postags) > 0:
        prepro_text = [token.lemma_ for token in tokens if token.pos_ in allowed_postags]
    else:
        prepro_text = [token.lemma_ for token in tokens]
    
    # Line breaks replaced by space because if replaced by nothing, words get concatenated.
    # prepro_text = [lemma.lower().replace('\n', '') for lemma in prepro_text]
    
    # Checks the aslist atribute in the function call. If True, returns a list of tokens. If False, returns a string of tokens separated by spaces.
    if aslist:
        return prepro_text
    else:
        return " ".join(prepro_text)


def preprocess_texts(input_texts,aslist=True, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'], disable_parser_ner=False):
    processed_texts = []
    for doc in input_texts:
        processed_doc = preprocess_text(doc, aslist, allowed_postags, disable_parser_ner)
        processed_texts.append(processed_doc)
    return processed_texts


# Code from https://www.youtube.com/watch?v=TKjjlp5_r7o
def lemmatization(texts, allowed_postags=['NOUN','ADJ', 'VERB', 'ADV']):
    nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
    texts_out = []
    for text in texts:
        doc = nlp(text)
        new_text = []
        for token in doc:
            if token.pos_ in allowed_postags:
                new_text.append(token.lemma_)
        final = " ".join(new_text)
        texts_out.append(final)
    return(texts_out)


# Code from https://www.youtube.com/watch?v=TKjjlp5_r7o
def gen_words(texts):
    final = []
    for text in texts:
        new = gensim.utils.simple_preprocess(text, deacc=True)
        final.append(new)
    return final