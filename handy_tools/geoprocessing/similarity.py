from functools import partial
from decimal import Decimal


# Similarity Index
import Levenshtein
import ngram

def ngram_similarity(base_locality_full, locality_full, ngram_size):
    ngram_instance = ngram.NGram(N=ngram_size)
    return ngram_instance.compare(base_locality_full, locality_full)

def levenshtein_similarity(base_locality_full, locality_full):
    if len(base_locality_full) == 0 and len(locality_full) == 0:
        return Decimal(1)
        
    distance = Levenshtein.distance(base_locality_full, locality_full)
    return Decimal(1) - Decimal(distance) / Decimal(max(len(base_locality_full), len(locality_full)))




SIMILARITY_METHODS = {
    "1-gram": partial(ngram_similarity, ngram_size=1),
    "2-gram": partial(ngram_similarity, ngram_size=2),
    "3-gram": partial(ngram_similarity, ngram_size=3),
    "levenshtein": levenshtein_similarity
}