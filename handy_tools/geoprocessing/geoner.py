import spacy

def get_geographic_entities(nlp, text):

    if not nlp:
        nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]

def ner_formatter(ner_list, model='en_core_web_sm', model_source='spacy'):
    ner_dictlist = []
    for ner in ner_list:
        item = {
            "ent": ner[0],
            "label": ner[1],
            "model": model,
            "model_source": model_source,
        }
        ner_dictlist.append(item)
    return ner_dictlist